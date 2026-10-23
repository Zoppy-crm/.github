import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import sys
import zlib

SCHEMA_VERSION = 1
BLOCK_PREFIX = '<!-- mutation-data v1 '
BLOCK_SUFFIX = ' -->'
BLOCK_RE = re.compile(r'<!-- mutation-data v(\d+) ([A-Za-z0-9+/=]+) -->')
BLOCK_LIMIT = 30000
STATUSES = ('ok', 'falhou', 'cancelado', 'nada-a-mutar')
COUNT_KEYS = (
    ('killed', 'Killed'),
    ('timeout', 'Timeout'),
    ('survived', 'Survived'),
    ('no_coverage', 'NoCoverage'),
    ('runtime_error', 'RuntimeError'),
    ('compile_error', 'CompileError'),
    ('ignored', 'Ignored'),
)


def _digest(*parts):
    return hashlib.sha256('\0'.join(str(p) for p in parts).encode()).hexdigest()[:12]


def mutant_id(path, mutator, start_line, start_col, end_line, end_col, replacement):
    return _digest(path, mutator, f'{start_line}:{start_col}-{end_line}:{end_col}', replacement)


def content_id(path, mutator, original, replacement):
    return _digest(path, mutator, re.sub(r'\s+', ' ', original or '').strip(), re.sub(r'\s+', ' ', replacement or '').strip())


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_iso(value):
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
    except (TypeError, ValueError):
        return None


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def meta_from_env(env=None):
    env = os.environ if env is None else env
    return {
        'repo': env.get('GITHUB_REPOSITORY'),
        'pr': _int(env.get('PR_NUMBER')),
        'head_sha': env.get('PR_HEAD_SHA') or None,
        'merge_sha': env.get('GITHUB_SHA') or None,
        'run_id': _int(env.get('GITHUB_RUN_ID')),
        'run_attempt': _int(env.get('GITHUB_RUN_ATTEMPT')),
        'started_at': env.get('MUTATION_STARTED_AT') or None,
    }


def _counts(raw):
    raw = raw or {}
    return {key: raw.get(status, 0) for key, status in COUNT_KEYS}


def _valid(counts):
    return sum(counts[k] for k in ('killed', 'timeout', 'survived', 'no_coverage', 'runtime_error', 'compile_error'))


def _score(counts, covered_only):
    detected = counts['killed'] + counts['timeout']
    total = detected + counts['survived'] + (0 if covered_only else counts['no_coverage'])
    return round(100.0 * detected / total, 1) if total else None


def _totals(files):
    totals = {key: 0 for key, _ in COUNT_KEYS}
    for f in files:
        for key in totals:
            totals[key] += (f.get('counts') or {}).get(key, 0)
    return {
        'valid': _valid(totals),
        'killed': totals['killed'],
        'timeout': totals['timeout'],
        'survived': totals['survived'],
        'no_coverage': totals['no_coverage'],
        'error': totals['runtime_error'] + totals['compile_error'],
        'ignored': totals['ignored'],
        'score_total': _score(totals, covered_only=False),
        'score_covered': _score(totals, covered_only=True),
    }


def _undetected_entry(path, mutant):
    mid = mutant.get('id') or mutant_id(
        path,
        mutant['mutator'],
        mutant['line'],
        mutant['column'],
        mutant.get('endLine', mutant['line']),
        mutant.get('endColumn', mutant['column']),
        mutant.get('replacement', ''),
    )
    cid = mutant.get('cid') or content_id(path, mutant['mutator'], mutant.get('original', ''), mutant.get('replacement', ''))
    return {
        'id': mid,
        'cid': cid,
        'line': mutant['line'],
        'col': mutant['column'],
        'mutator': mutant['mutator'],
        'status': mutant['status'],
    }


def _file_status(entry):
    if entry.get('skipped') == 'sem spec':
        return 'sem-spec'
    if entry.get('skipped') == 'fora do teto':
        return 'fora-do-teto'
    if 'error' in entry:
        return 'erro'
    return 'ok'


def _caps(files):
    capped = [f for f in files if f.get('skipped') == 'fora do teto']
    reasons = [f.get('skipReason') or '' for f in capped]
    time_hit = any(r.startswith('tempo') for r in reasons) or any('orçamento' in (f.get('error') or '') for f in files)
    return {
        'time': time_hit,
        'mutants': any(r.startswith('mutantes') for r in reasons),
        'capped_files': len(capped),
    }


def build(status, meta, summary=None, finished_at=None):
    if status not in STATUSES:
        raise ValueError(f'status inválido: {status}')
    finished_at = finished_at or now_iso()
    started = parse_iso(meta.get('started_at'))
    finished = parse_iso(finished_at)
    data = {
        'v': SCHEMA_VERSION,
        'repo': meta.get('repo'),
        'pr': meta.get('pr'),
        'head_sha': meta.get('head_sha'),
        'merge_sha': meta.get('merge_sha'),
        'base_sha': None,
        'run_id': meta.get('run_id'),
        'run_attempt': meta.get('run_attempt'),
        'started_at': meta.get('started_at'),
        'finished_at': finished_at,
        'duration_s': round((finished - started).total_seconds()) if started and finished else None,
        'stryker_s': None,
        'status': status,
        'caps': {'time': False, 'mutants': False, 'capped_files': 0},
        'limits': None,
        'totals': _totals([]),
        'files': [],
        'truncated': False,
        'killed_truncated': False,
    }
    if not summary:
        return data
    files = []
    for entry in summary.get('files', []):
        path = entry['file']
        counts = _counts(entry.get('counts'))
        files.append(
            {
                'path': path,
                'status': _file_status(entry),
                'counts': counts,
                'seconds': entry.get('seconds'),
                'undetected': [_undetected_entry(path, m) for m in entry.get('undetected', [])],
                'killed': list(entry.get('killedIds', [])),
            }
        )
    data.update(
        {
            'base_sha': summary.get('base'),
            'stryker_s': summary.get('seconds'),
            'caps': _caps(summary.get('files', [])),
            'limits': {'budget_min': summary.get('budgetMin'), 'max_mutants': summary.get('maxMutants')},
            'totals': _totals(files),
            'files': files,
        }
    )
    return data


def encode(data):
    raw = json.dumps(data, separators=(',', ':'), ensure_ascii=False, sort_keys=True).encode()
    payload = base64.b64encode(zlib.compress(raw, 9)).decode('ascii')
    return f'{BLOCK_PREFIX}{payload}{BLOCK_SUFFIX}'


def decode(text):
    matches = BLOCK_RE.findall(text or '')
    if not matches:
        return None
    version, payload = matches[-1]
    data = json.loads(zlib.decompress(base64.b64decode(payload)).decode())
    data.setdefault('v', int(version))
    return data


def _drop_last(files, key):
    for f in reversed(files):
        if f[key]:
            f[key].pop()
            return True
    return False


def fit(data, limit=BLOCK_LIMIT):
    block = encode(data)
    if len(block) <= limit:
        return block
    data = json.loads(json.dumps(data))
    for key, flag in (('killed', 'killed_truncated'), ('undetected', 'truncated')):
        data[flag] = True
        while len(block) > limit:
            total = sum(len(f[key]) for f in data['files'])
            if not total:
                break
            drop = max(1, total // 10)
            for _ in range(drop):
                _drop_last(data['files'], key)
            block = encode(data)
        if len(block) <= limit:
            return block
    return block


def summary_from_selection(selection):
    return {'files': [{'file': f['file'], 'skipped': 'sem spec'} for f in selection.get('files', []) if not f.get('spec')]}


def load_json(path):
    if not path or not os.path.isfile(path):
        return None
    with open(path) as handle:
        return json.load(handle)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--status', choices=STATUSES)
    parser.add_argument('--summary')
    parser.add_argument('--selection')
    parser.add_argument('--extract')
    parser.add_argument('--limit', type=int, default=BLOCK_LIMIT)
    args = parser.parse_args()
    if args.extract:
        with open(args.extract) as handle:
            data = decode(handle.read())
        if data is None:
            sys.exit(1)
        sys.stdout.write(json.dumps(data, ensure_ascii=False) + '\n')
        return
    if not args.status:
        parser.error('--status é obrigatório')
    summary = load_json(args.summary)
    if summary is None and args.selection:
        selection = load_json(args.selection)
        summary = summary_from_selection(selection) if selection else None
    sys.stdout.write(fit(build(args.status, meta_from_env(), summary), args.limit) + '\n')


if __name__ == '__main__':
    main()
