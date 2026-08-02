#!/usr/bin/env python3
"""Summarize append-only deltas from a Claude Code JSONL transcript.

The default output contains metadata, not message bodies. It is safe to use as a
cursor/inventory aid, but it does not replace inspection of the relevant raw
records and current repository state.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable


LIMIT_RE = re.compile(
    r"(usage limit|rate limit|allowance|weekly limit|resets? at|credit[s]? exhausted)",
    re.IGNORECASE,
)
FAIL_RE = re.compile(
    r"(^|\\s)(fatal:|exit(?:ed)?[ =:]+(?:1|[2-9]|[1-9][0-9]+)|"
    r"exit_code[ =:]+(?:1|[2-9]|[1-9][0-9]+)|killed|terminated|failed)(\\s|$)",
    re.IGNORECASE,
)
TASK_TAG_RE = re.compile(r"<(task-id|status|summary)>(.*?)</\1>", re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--session", help="Claude session UUID or unique prefix")
    source.add_argument("--path", type=Path, help="Exact transcript JSONL path")
    parser.add_argument(
        "--projects-root",
        type=Path,
        default=Path.home() / ".claude" / "projects",
        help="Claude projects root (default: ~/.claude/projects)",
    )
    parser.add_argument(
        "--after-line",
        type=int,
        default=0,
        help="Read records strictly after this 1-based line number",
    )
    parser.add_argument(
        "--state",
        type=Path,
        help="Optional cursor JSON. Its cursor is used unless --after-line is nonzero.",
    )
    parser.add_argument(
        "--advance",
        action="store_true",
        help="Persist the resulting cursor to --state after successful parsing",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format (default: json)",
    )
    return parser.parse_args()


def resolve_path(args: argparse.Namespace) -> Path:
    if args.path:
        path = args.path.expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"transcript does not exist: {path}")
        return path

    prefix = args.session.lower()
    matches = [
        path.resolve()
        for path in args.projects_root.expanduser().glob("*/*.jsonl")
        if path.stem.lower().startswith(prefix)
    ]
    if not matches:
        raise ValueError(f"no Claude transcript matched session prefix {args.session!r}")
    if len(matches) > 1:
        listing = "\n".join(f"  - {path}" for path in matches)
        raise ValueError(
            f"session prefix {args.session!r} is ambiguous; matches:\n{listing}"
        )
    return matches[0]


def load_state(path: Path | None, transcript: Path) -> int:
    if path is None or not path.exists():
        return 0
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read cursor state {path}: {exc}") from exc
    recorded = Path(state.get("transcript", "")).expanduser()
    if recorded and recorded.resolve() != transcript.resolve():
        raise ValueError(
            f"cursor state targets {recorded}, not requested transcript {transcript}"
        )
    cursor = state.get("cursor_line", 0)
    if not isinstance(cursor, int) or cursor < 0:
        raise ValueError(f"invalid cursor_line in {path}: {cursor!r}")
    return cursor


def iter_text(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_text(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {"thinking", "signature"}:
                continue
            yield from iter_text(item)


def collect_task_notification(text: str, line: int) -> dict[str, Any] | None:
    if "<task-notification>" not in text:
        return None
    fields = {key: value.strip() for key, value in TASK_TAG_RE.findall(text)}
    return {
        "line": line,
        "task_id": fields.get("task-id"),
        "status": fields.get("status"),
        "summary": fields.get("summary"),
    }


def summarize(path: Path, after_line: int) -> dict[str, Any]:
    counts: collections.Counter[str] = collections.Counter()
    models: collections.Counter[str] = collections.Counter()
    task_notifications: list[dict[str, Any]] = []
    pr_links: list[dict[str, Any]] = []
    limit_signal_lines: list[int] = []
    failure_signal_lines: list[int] = []
    timestamps: list[str] = []
    cwd_values: collections.Counter[str] = collections.Counter()
    branches: collections.Counter[str] = collections.Counter()
    session_ids: collections.Counter[str] = collections.Counter()
    malformed: list[int] = []
    last_line = 0
    parsed = 0

    with path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            last_line = line_no
            if line_no <= after_line:
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError:
                malformed.append(line_no)
                continue

            parsed += 1
            event_type = str(record.get("type", "unknown"))
            counts[event_type] += 1
            for key, counter in (
                ("cwd", cwd_values),
                ("gitBranch", branches),
                ("sessionId", session_ids),
            ):
                value = record.get(key)
                if isinstance(value, str) and value:
                    counter[value] += 1

            timestamp = record.get("timestamp")
            if isinstance(timestamp, str):
                timestamps.append(timestamp)

            message = record.get("message")
            if isinstance(message, dict):
                model = message.get("model")
                if isinstance(model, str) and model:
                    models[model] += 1

            if event_type == "pr-link":
                pr_links.append(
                    {
                        "line": line_no,
                        "repository": record.get("prRepository"),
                        "number": record.get("prNumber"),
                        "url": record.get("prUrl"),
                    }
                )

            texts = list(iter_text(record))
            combined = "\n".join(texts)
            notification = collect_task_notification(combined, line_no)
            if notification:
                task_notifications.append(notification)
            if LIMIT_RE.search(combined):
                limit_signal_lines.append(line_no)
            if FAIL_RE.search(combined):
                failure_signal_lines.append(line_no)

    has_delta = last_line > after_line
    return {
        "transcript": str(path),
        "from_line": after_line + 1 if has_delta else None,
        "to_line": last_line,
        "parsed_records": parsed,
        "malformed_lines": malformed,
        "time_range": {
            "first": min(timestamps) if timestamps else None,
            "last": max(timestamps) if timestamps else None,
        },
        "event_counts": dict(sorted(counts.items())),
        "session_ids": dict(session_ids.most_common()),
        "cwd_values": dict(cwd_values.most_common()),
        "git_branches": dict(branches.most_common()),
        "observed_models": dict(models.most_common()),
        "fable_verified_in_delta": any(
            model.startswith("claude-fable-") for model in models
        ),
        "task_notifications": task_notifications,
        "pr_links": pr_links,
        "possible_limit_signal_lines": limit_signal_lines,
        "possible_failure_signal_lines": failure_signal_lines,
        "cursor_line": last_line,
    }


def markdown(data: dict[str, Any]) -> str:
    def items(mapping: dict[str, Any]) -> str:
        return ", ".join(f"`{key}` × {value}" for key, value in mapping.items()) or "none"

    lines = [
        "# Claude transcript delta",
        "",
        f"- Transcript: `{data['transcript']}`",
        (
            f"- Lines: {data['from_line']}-{data['to_line']}"
            if data["from_line"] is not None
            else f"- Lines: no records after cursor {data['cursor_line']}"
        ),
        f"- Parsed records: {data['parsed_records']}",
        f"- Event time range: {data['time_range']['first']} → {data['time_range']['last']}",
        f"- Models: {items(data['observed_models'])}",
        f"- Fable verified in this delta: {'yes' if data['fable_verified_in_delta'] else 'no'}",
        f"- Cwds: {items(data['cwd_values'])}",
        f"- Branch labels: {items(data['git_branches'])}",
        f"- Event counts: {items(data['event_counts'])}",
        f"- Possible allowance/limit signal lines: {data['possible_limit_signal_lines'] or 'none'}",
        f"- Possible failure signal lines: {data['possible_failure_signal_lines'] or 'none'}",
        f"- Malformed JSONL lines: {data['malformed_lines'] or 'none'}",
        "",
        "## Task notifications",
        "",
    ]
    if data["task_notifications"]:
        for task in data["task_notifications"]:
            lines.append(
                f"- Line {task['line']}: `{task['task_id']}` — "
                f"{task['status'] or 'unknown'} — {task['summary'] or 'no summary'}"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## PR links", ""])
    if data["pr_links"]:
        unique_prs: dict[str, dict[str, Any]] = {}
        for pr in data["pr_links"]:
            if pr["url"]:
                unique_prs[pr["url"]] = pr
        for pr in unique_prs.values():
            label = f"{pr['repository']}#{pr['number']}"
            lines.append(f"- Line {pr['line']}: [{label}]({pr['url']})")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "> Signal lines are search hints, not adjudicated findings. Inspect the raw",
            "> records and reconcile them with current process, Git, log, and PR state.",
        ]
    )
    return "\n".join(lines)


def save_state(path: Path, transcript: Path, cursor: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "transcript": str(transcript),
        "cursor_line": cursor,
        "transcript_inode": os.stat(transcript).st_ino,
    }
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    args = parse_args()
    try:
        transcript = resolve_path(args)
        state_cursor = load_state(args.state, transcript)
        after_line = args.after_line or state_cursor
        data = summarize(transcript, after_line)
        if args.advance:
            if args.state is None:
                raise ValueError("--advance requires --state")
            save_state(args.state, transcript, data["cursor_line"])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        print(markdown(data))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
