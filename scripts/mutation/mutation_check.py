import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

MARKER = '<!-- mutation-check -->'
COMMENT_LIMIT = 65000
MAX_LISTED = 80
DETECTED = ('Killed', 'Timeout')
UNDETECTED = ('Survived', 'NoCoverage')
ERROR_STATUSES = ('RuntimeError', 'CompileError')
STATUSES = DETECTED + UNDETECTED + ('Ignored',) + ERROR_STATUSES
EXCLUDED_MUTATIONS = ['StringLiteral', 'OptionalChaining', 'ArrayDeclaration']
EXCLUDED_SUFFIXES = (
    '.spec.ts',
    '.d.ts',
    '.module.ts',
    '.dto.ts',
    '.enum.ts',
    '.interface.ts',
    '.model.ts',
    '.request.ts',
    '.response.ts',
    '.types.ts',
    '.constants.ts',
)
EXCLUDED_BASENAMES = ('index.ts', 'types.ts')
IGNORER_PLUGIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log-service-ignorer.mjs')
HUNK_RE = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@')
ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
LOG_LINE_RE = re.compile(r'^\d{2}:\d{2}:\d{2} \(\d+\) [A-Z]+ ')
LOG_ERROR_RE = re.compile(r'^\d{2}:\d{2}:\d{2} \(\d+\) ERROR ')
STACK_RE = re.compile(r'^\s*at ')
SANDBOX_RE = re.compile(r'\.stryker-tmp/sandbox-[^/]+/')
GENERIC_ERROR = 'Stryker '
SWITCH_CASE_RE = re.compile(r'^(case\b.*|default\s*):$', re.S)


def env_default(name, fallback, cast):
    value = os.environ.get(name)
    return cast(value) if value not in (None, '') else fallback


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--head', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--cache', default=os.environ.get('MUTATION_CACHE_DIR'))
    parser.add_argument('--concurrency', type=int, default=env_default('MUTATION_CONCURRENCY', 4, int))
    parser.add_argument('--budget-min', type=float, default=env_default('MUTATION_BUDGET_MIN', 55, float))
    parser.add_argument('--margin-min', type=float, default=env_default('MUTATION_MARGIN_MIN', 5, float))
    parser.add_argument('--max-mutants', type=int, default=env_default('MUTATION_MAX_MUTANTS', 600, int))
    parser.add_argument('--only', nargs='+', default=[])
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not args.cache:
        parser.error('--cache (ou MUTATION_CACHE_DIR) é obrigatório')
    return args


def git(repo, *args):
    return subprocess.run(['git', '-C', repo, *args], check=True, capture_output=True, text=True).stdout


def is_logic_file(path):
    if not path.startswith('src/') or not path.endswith('.ts'):
        return False
    if path.startswith('src/db/') or '/fixtures/' in path:
        return False
    if path.endswith(EXCLUDED_SUFFIXES):
        return False
    return os.path.basename(path) not in EXCLUDED_BASENAMES


def merge_ranges(ranges):
    merged = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(r) for r in merged]


def changed_ranges(repo, base, head, path):
    ranges = []
    for line in git(repo, 'diff', '-U0', base, head, '--', path).splitlines():
        match = HUNK_RE.match(line)
        if not match:
            continue
        start = int(match.group(1))
        count = int(match.group(2)) if match.group(2) is not None else 1
        if count > 0:
            ranges.append((start, start + count - 1))
    return merge_ranges(ranges)


def count_lines(repo, head, path):
    return git(repo, 'show', f'{head}:{path}').count('\n') or 1


def select_files(repo, base, head, only):
    merge_base = git(repo, 'merge-base', base, head).strip()
    status_lines = git(repo, 'diff', '--diff-filter=AM', '--name-status', f'{merge_base}...{head}', '--', 'src').splitlines()
    selected = []
    for line in status_lines:
        status, path = line.split('\t', 1)
        if not is_logic_file(path):
            continue
        if status.startswith('A'):
            ranges = None
            changed = count_lines(repo, head, path)
        else:
            ranges = changed_ranges(repo, merge_base, head, path)
            if not ranges:
                continue
            changed = sum(end - start + 1 for start, end in ranges)
        spec = path[:-3] + '.spec.ts'
        selected.append(
            {
                'file': path,
                'added': status.startswith('A'),
                'ranges': ranges,
                'changedLines': changed,
                'spec': spec if os.path.isfile(os.path.join(repo, spec)) else None,
            }
        )
    if only:
        wanted = set(only)
        missing = wanted - {s['file'] for s in selected}
        for path in sorted(missing):
            print(f'aviso: {path} não está entre os arquivos selecionados do diff', file=sys.stderr)
        selected = [s for s in selected if s['file'] in wanted]
    selected.sort(key=lambda s: (-s['changedLines'], s['file']))
    return merge_base, selected


def mutate_patterns(item):
    if item['ranges'] is None:
        return [item['file']]
    return [f"{item['file']}:{start}-{end}" for start, end in item['ranges']]


def slug(path):
    return re.sub(r'[^a-zA-Z0-9]+', '-', path[4:-3]).strip('-')


def stryker_config(item, args, report_path):
    return {
        'testRunner': 'jest',
        'jest': {
            'enableFindRelatedTests': False,
            'config': {'testRegex': '/' + re.escape(item['spec'][4:]) + '$'},
        },
        'coverageAnalysis': 'perTest',
        'mutate': mutate_patterns(item),
        'ignoreStatic': True,
        'timeoutMS': 30000,
        'disableTypeChecks': 'src/**/*.ts',
        'concurrency': args.concurrency,
        'mutator': {'excludedMutations': EXCLUDED_MUTATIONS},
        'plugins': ['@stryker-mutator/*', IGNORER_PLUGIN],
        'ignorers': ['log-service'],
        'incremental': True,
        'incrementalFile': os.path.join(os.path.abspath(args.cache), slug(item['file']) + '.json'),
        'reporters': ['json'],
        'jsonReporter': {'fileName': report_path},
        'tempDirName': '.stryker-tmp',
        'cleanTempDir': True,
        'logLevel': 'info',
        'dryRunTimeoutMinutes': 15,
    }


def source_snippet(source_lines, location):
    start, end = location['start'], location['end']
    if not 0 < start['line'] <= end['line'] <= len(source_lines):
        return ''
    if start['line'] == end['line']:
        return source_lines[start['line'] - 1][start['column'] - 1 : end['column'] - 1]
    parts = [source_lines[start['line'] - 1][start['column'] - 1 :]]
    parts += source_lines[start['line'] : end['line'] - 1]
    parts.append(source_lines[end['line'] - 1][: end['column'] - 1])
    return '\n'.join(parts)


def read_report(report_path, source_file):
    with open(report_path) as handle:
        report = json.load(handle)
    counts = collections.Counter()
    undetected = []
    for path, data in report['files'].items():
        source_lines = data.get('source', '').split('\n')
        for mutant in data['mutants']:
            counts[mutant['status']] += 1
            if mutant['status'] not in UNDETECTED:
                continue
            location = mutant['location']
            undetected.append(
                {
                    'line': location['start']['line'],
                    'column': location['start']['column'],
                    'status': mutant['status'],
                    'mutator': mutant['mutatorName'],
                    'original': source_snippet(source_lines, location),
                    'replacement': mutant.get('replacement', ''),
                }
            )
    undetected.sort(key=lambda m: (m['line'], m['column']))
    return {status: counts.get(status, 0) for status in STATUSES}, undetected


def tail(path, lines=25):
    try:
        with open(path, errors='replace') as handle:
            return ''.join(handle.readlines()[-lines:])
    except OSError:
        return ''


def clean_log_line(line, repo):
    line = SANDBOX_RE.sub('', ANSI_RE.sub('', line).rstrip())
    return line.replace(repo.rstrip('/') + '/', '')


def error_excerpt(path, repo, max_lines=8, width=220):
    try:
        with open(path, errors='replace') as handle:
            lines = [clean_log_line(line, repo) for line in handle]
    except OSError:
        return []
    blocks = []
    index = 0
    while index < len(lines):
        if not LOG_ERROR_RE.match(lines[index]):
            index += 1
            continue
        block = [LOG_ERROR_RE.sub('', lines[index]).strip()]
        frame_taken = False
        index += 1
        while index < len(lines) and lines[index].strip() and not LOG_LINE_RE.match(lines[index]):
            line = lines[index].strip()
            index += 1
            if STACK_RE.match(line):
                if not frame_taken and 'node_modules' not in line and 'src/' in line:
                    block.append(line)
                    frame_taken = True
                continue
            block.append(line)
        blocks.append(block)
    specific = [b for b in blocks if not b[0].startswith(GENERIC_ERROR)]
    chosen = (specific or blocks)[:1]
    if not chosen:
        chosen = [[line.strip() for line in lines if line.strip()][-5:]]
    excerpt = [line if len(line) <= width else line[: width - 1] + '…' for block in chosen for line in block]
    if len(excerpt) > max_lines:
        excerpt = excerpt[:max_lines] + ['…']
    return excerpt


def run_file(item, args, work_dir, out_dir, timeout):
    name = slug(item['file'])
    report_path = os.path.join(out_dir, 'reports', name + '.json')
    log_path = os.path.join(out_dir, 'logs', name + '.log')
    config_path = os.path.join(work_dir, name + '.stryker.json')
    if os.path.exists(report_path):
        os.remove(report_path)
    with open(config_path, 'w') as handle:
        json.dump(stryker_config(item, args, report_path), handle, indent=1)
    env = dict(os.environ, TZ='America/Sao_Paulo', AWS_SDK_JS_SUPPRESS_MAINTENANCE_MODE_MESSAGE='1')
    started = time.time()
    result = {'rc': None}
    with open(log_path, 'w') as log:
        process = subprocess.Popen(
            ['nice', '-n', '19', 'npx', 'stryker', 'run', config_path],
            cwd=args.repo,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            result['rc'] = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, 9)
            process.wait()
            result['error'] = 'estourou o tempo restante do orçamento'
    result['seconds'] = round(time.time() - started, 1)
    if result['rc'] == 0 and os.path.exists(report_path):
        result['counts'], result['undetected'] = read_report(report_path, item['file'])
    elif 'error' not in result:
        result['error'] = f"stryker saiu com código {result['rc']}"
    if 'error' in result:
        result['logTail'] = tail(log_path)
        result['errorExcerpt'] = error_excerpt(log_path, args.repo)
    return result


def valid_mutants(counts):
    return sum(counts[s] for s in DETECTED + UNDETECTED + ERROR_STATUSES)


def score(counts, covered_only):
    detected = sum(counts[s] for s in DETECTED)
    total = detected + counts['Survived'] + (0 if covered_only else counts['NoCoverage'])
    return round(100.0 * detected / total, 1) if total else None


def run_all(args, selection):
    os.makedirs(os.path.join(args.out, 'reports'), exist_ok=True)
    os.makedirs(os.path.join(args.out, 'logs'), exist_ok=True)
    os.makedirs(args.cache, exist_ok=True)
    work_dir = tempfile.mkdtemp(prefix='mutation-check-')
    budget = args.budget_min * 60
    margin = args.margin_min * 60
    started = time.time()
    mutants_so_far = 0
    results = []
    try:
        for item in selection:
            entry = {'file': item['file'], 'spec': item['spec'], 'changedLines': item['changedLines'], 'mutate': mutate_patterns(item)}
            results.append(entry)
            if item['spec'] is None:
                entry['skipped'] = 'sem spec'
                continue
            elapsed = time.time() - started
            if elapsed > budget - margin:
                entry['skipped'] = 'fora do teto'
                entry['skipReason'] = f'tempo: {round(elapsed / 60, 1)} min de {args.budget_min:g}'
                continue
            if mutants_so_far >= args.max_mutants:
                entry['skipped'] = 'fora do teto'
                entry['skipReason'] = f'mutantes: {mutants_so_far} de {args.max_mutants}'
                continue
            print(f"[{round(elapsed)}s] {item['file']} ({len(entry['mutate'])} faixas)", flush=True)
            entry.update(run_file(item, args, work_dir, args.out, timeout=max(budget - elapsed, 60)))
            if 'counts' in entry:
                mutants_so_far += valid_mutants(entry['counts'])
                print(f"    {entry['seconds']}s {json.dumps(entry['counts'])}", flush=True)
            else:
                print(f"    {entry['seconds']}s ERRO {entry['error']}", flush=True)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
    totals = collections.Counter()
    for entry in results:
        totals.update(entry.get('counts', {}))
    totals = {status: totals.get(status, 0) for status in STATUSES}
    return {
        'seconds': round(time.time() - started, 1),
        'budgetMin': args.budget_min,
        'maxMutants': args.max_mutants,
        'concurrency': args.concurrency,
        'totals': totals,
        'score': score(totals, covered_only=False),
        'scoreCovered': score(totals, covered_only=True),
        'files': results,
    }


def fmt_seconds(seconds):
    seconds = int(round(seconds))
    if seconds < 60:
        return f'{seconds}s'
    minutes, rest = divmod(seconds, 60)
    return f'{minutes}min {rest:02d}s'


def fmt_score(value):
    return '—' if value is None else f'{value:.1f}%'.replace('.', ',')


def plural(count, singular, plural_form):
    return f'{count} {singular if count == 1 else plural_form}'


def killed(counts):
    return counts['Killed'] + counts['Timeout']


def error_mutants(counts):
    return sum(counts[s] for s in ERROR_STATUSES)


def collapse(text):
    return re.sub(r'\s+', ' ', text).strip()


def inline_code(text, limit=140):
    text = collapse(text)
    if len(text) > limit:
        text = text[: limit - 1] + '…'
    if not text:
        return '*(vazio)*'
    fence = '``' if '`' in text else '`'
    pad = ' ' if fence == '``' or text.startswith('`') or text.endswith('`') else ''
    return f'{fence}{pad}{text}{pad}{fence}'


def describe_mutation(mutant):
    original = collapse(mutant['original'])
    replacement = collapse(mutant['replacement'])
    if mutant['mutator'] == 'ConditionalExpression' and SWITCH_CASE_RE.match(replacement) and original != replacement:
        return f'{inline_code(original, 90)} → *case sem corpo*'
    if original == replacement:
        return f'{inline_code(original, 90)} → *(sem diferença no texto)*'
    return f'{inline_code(original, 90)} → {inline_code(replacement, 90)}'


def mutant_lines(mutants):
    by_line = collections.OrderedDict()
    for m in mutants:
        by_line.setdefault(m['line'], collections.OrderedDict())
        key = (m['mutator'], m['status'], describe_mutation(m))
        by_line[m['line']].setdefault(key, []).append(m['column'])
    out = []
    for line, entries in by_line.items():
        rendered = []
        for (mutator, status, text), columns in entries.items():
            kind = 'sobrevivente' if status == 'Survived' else 'sem cobertura'
            count = f' ×{len(columns)}' if len(columns) > 1 else ''
            cols = ', '.join(str(c) for c in sorted(set(columns)))
            rendered.append((cols, f'{mutator} · {kind}: {text}{count}'))
        if len(rendered) == 1:
            out.append(f'- linha {line}, col {rendered[0][0]} · {rendered[0][1]}')
            continue
        out.append(f'- linha {line}')
        out += [f'  - col {cols} · {text}' for cols, text in rendered]
    return out


def code_block(lines):
    text = '\n'.join(lines)
    fence = '````' if '```' in text else '```'
    return [fence + 'text', text, fence]


def render_failures(failed):
    groups = collections.OrderedDict()
    for f in failed:
        groups.setdefault(tuple(f.get('errorExcerpt') or ()), []).append(f)
    out = ['### Falharam ao rodar', '']
    for excerpt, files in groups.items():
        for f in files:
            out.append(f"- `{f['file'][4:]}`: {f['error']}")
        out.append('')
        if excerpt:
            out += code_block(excerpt)
            out.append('')
    out.append('_O log completo de cada arquivo está na execução, pelo link no fim do comentário._')
    out.append('')
    return out


def render_comment(summary, max_listed):
    totals = summary['totals']
    ran = [f for f in summary['files'] if 'counts' in f]
    with_mutants = [f for f in ran if valid_mutants(f['counts'])]
    empty = [f for f in ran if not valid_mutants(f['counts'])]
    failed = [f for f in summary['files'] if 'error' in f]
    no_spec = [f for f in summary['files'] if f.get('skipped') == 'sem spec']
    capped = [f for f in summary['files'] if f.get('skipped') == 'fora do teto']
    with_errors = any(error_mutants(f['counts']) for f in with_mutants)
    out = [MARKER, '## Teste de mutação', '']
    out.append('> Informativo: este check **nunca bloqueia o merge**.')
    out.append('')
    out.append(
        f"**Score:** {fmt_score(summary['score'])} no total · {fmt_score(summary['scoreCovered'])} no código coberto por teste · "
        f"**Tempo:** {fmt_seconds(summary['seconds'])}"
    )
    out.append('')
    if with_mutants:
        parts = [
            plural(killed(totals), 'morto', 'mortos'),
            plural(totals['Survived'], 'sobrevivente', 'sobreviventes'),
            f"{totals['NoCoverage']} sem cobertura",
        ]
        if error_mutants(totals):
            parts.append(f'{error_mutants(totals)} com erro (o spec quebrou fora de um teste ou o mutante não compila)')
        out.append(
            f"{plural(valid_mutants(totals), 'mutante', 'mutantes')} em {plural(len(with_mutants), 'arquivo', 'arquivos')}: "
            f"{', '.join(parts)}. Fora da conta, {plural(totals['Ignored'], 'ignorado', 'ignorados')} "
            '(chamadas ao LogService, estáticos ou mutadores desligados).'
        )
        out.append('')
    elif ran:
        out.append('Nenhum mutante nas linhas alteradas.')
        out.append('')
    out.append(
        'Como ler: cada mutante é uma pequena mudança de comportamento nas linhas alteradas pelo PR. '
        'Um mutante **sobrevivente** é uma mudança que nenhum teste do spec irmão pegou; **sem cobertura** '
        'é código que o spec nem executa. Nem todo sobrevivente é bug: pode ser um mutante equivalente '
        '(mesmo comportamento observável). Só o spec irmão roda contra cada arquivo, então um sobrevivente '
        'pode estar coberto por outro spec (por exemplo, um sobrevivente no domain que o spec do application pega).'
    )
    out.append('')
    if with_mutants:
        header = '| Arquivo | Mutantes | Mortos | Sobreviventes | Sem cobertura |'
        align = '|---|---:|---:|---:|---:|'
        if with_errors:
            header += ' Erro |'
            align += '---:|'
        out.append(header + ' Tempo |')
        out.append(align + '---:|')
        for f in with_mutants:
            c = f['counts']
            row = f"| `{f['file'][4:]}` | {valid_mutants(c)} | {killed(c)} | {c['Survived']} | {c['NoCoverage']} |"
            if with_errors:
                row += f' {error_mutants(c)} |'
            out.append(row + f" {fmt_seconds(f['seconds'])} |")
        out.append('')
    if empty:
        verb = 'rodou' if len(empty) == 1 else 'rodaram'
        out.append(f"_{plural(len(empty), 'arquivo', 'arquivos')} {verb} sem mutante nas linhas alteradas e não {'aparece' if len(empty) == 1 else 'aparecem'} na tabela._")
        out.append('')
    listed = 0
    total_undetected = sum(len(f['undetected']) for f in ran)
    blocks = []
    for f in with_mutants:
        if not f['undetected'] or listed >= max_listed:
            continue
        take = f['undetected'][: max_listed - listed]
        listed += len(take)
        c = f['counts']
        block = [
            '<details>',
            f"<summary><code>{f['file'][4:]}</code>: {plural(c['Survived'], 'sobrevivente', 'sobreviventes')}, {c['NoCoverage']} sem cobertura</summary>",
            '',
        ]
        block += mutant_lines(take)
        if len(take) < len(f['undetected']):
            block.append(f"- … mais {len(f['undetected']) - len(take)} neste arquivo")
        block += ['', '</details>', '']
        blocks.append(block)
    if blocks:
        out.append('### Sobreviventes e sem cobertura')
        out.append('')
        for block in blocks:
            out += block
        if listed < total_undetected:
            omitted = total_undetected - listed
            out.append(f"_{plural(omitted, 'mutante omitido', 'mutantes omitidos')} da lista; o detalhe completo está na execução, pelo link no fim do comentário._")
            out.append('')
    if failed:
        out += render_failures(failed)
    if no_spec:
        out.append(f'### Sem spec irmão ({len(no_spec)})')
        out.append('')
        out.append('Arquivos alterados sem `.spec.ts` na mesma pasta; não foram mutados.')
        out.append('')
        for f in no_spec:
            out.append(f"- `{f['file'][4:]}`")
        out.append('')
    if capped:
        out.append(f'### Fora do teto ({len(capped)})')
        out.append('')
        out.append(f"Não rodaram por limite de tempo ({summary['budgetMin']:g} min) ou de mutantes ({summary['maxMutants']}).")
        out.append('')
        for f in capped:
            out.append(f"- `{f['file'][4:]}` ({f['skipReason']})")
        out.append('')
    return '\n'.join(out)


def build_comment(summary):
    max_listed = MAX_LISTED
    while True:
        comment = render_comment(summary, max_listed)
        if len(comment) <= COMMENT_LIMIT or max_listed == 0:
            break
        max_listed //= 2
    if len(comment) > COMMENT_LIMIT:
        cut = comment.rfind('\n', 0, COMMENT_LIMIT - 200)
        comment = comment[:cut] + '\n\n_Comentário truncado pelo limite do GitHub; o detalhe completo está na execução, pelo link no fim do comentário._\n'
    return comment


def print_selection(merge_base, selection):
    print(f'merge-base: {merge_base}')
    with_spec = [s for s in selection if s['spec']]
    without = [s for s in selection if not s['spec']]
    print(f'{len(selection)} arquivos de lógica, {len(with_spec)} com spec irmão, {len(without)} sem spec')
    print(f'{sum(len(mutate_patterns(s)) for s in selection)} faixas')
    for s in selection:
        print(f"{s['changedLines']:5d}  {s['file']}  spec={'sim' if s['spec'] else 'NÃO'}")
        for pattern in mutate_patterns(s):
            print(f'         {pattern}')


def main():
    args = parse_args()
    args.repo = os.path.abspath(args.repo)
    args.out = os.path.abspath(args.out)
    args.cache = os.path.abspath(args.cache)
    merge_base, selection = select_files(args.repo, args.base, args.head, args.only)
    if args.dry_run:
        print_selection(merge_base, selection)
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, 'selection.json'), 'w') as handle:
            json.dump({'base': merge_base, 'head': args.head, 'files': selection}, handle, indent=1, ensure_ascii=False)
        return
    summary = run_all(args, selection)
    summary['base'] = merge_base
    summary['head'] = args.head
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, 'summary.json'), 'w') as handle:
        json.dump(summary, handle, indent=1, ensure_ascii=False)
    with open(os.path.join(args.out, 'comment.md'), 'w') as handle:
        handle.write(build_comment(summary))
    print(f"total {summary['seconds']}s score={summary['score']} coberto={summary['scoreCovered']} {json.dumps(summary['totals'])}")


if __name__ == '__main__':
    main()
