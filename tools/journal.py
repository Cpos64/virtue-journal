from __future__ import annotations

import sys
import re
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPO_ROOT / "templates" / "daily.md"
ENTRIES_ROOT = REPO_ROOT / "entries"

VIRTUES = [
    "Silence",
    "Frugality",
    "Industry",
    "Humility",
    "Mindfulness",
    "Contentment",
    "Abstinence",
    "Purity",
    "Wisdom",
    "Moderation",
]


def entry_path_for(d: date) -> Path:
    yyyy = f"{d.year:04d}"
    mm = f"{d.month:02d}"
    dd = f"{d.day:02d}"
    return ENTRIES_ROOT / yyyy / mm / f"{yyyy}-{mm}-{dd}.md"


def render_daily_template(d: date) -> str:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.replace("{{DATE}}", d.isoformat())


def init_today(force_if_empty: bool = True) -> Path:
    d = date.today()
    out_path = entry_path_for(d)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists():
        if force_if_empty:
            existing = out_path.read_text(encoding="utf-8", errors="ignore")
            if existing.strip() == "":
                out_path.write_text(render_daily_template(d), encoding="utf-8")
        return out_path

    out_path.write_text(render_daily_template(d), encoding="utf-8")
    return out_path


def ask_yn(prompt: str) -> str:
    """Return 'Y' or 'N'."""
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in {"y", "yes"}:
            return "Y"
        if ans in {"n", "no"}:
            return "N"
        print("Please type y or n.")


def replace_yn_for_label(text: str, label_phrase: str, value: str) -> str:
    """
    Replace the first '(Y/N)' that appears on a line containing label_phrase
    with '(Y)' or '(N)'.

    Example line in markdown:
      - **Did you get to bed on time?** (Y/N)

    We match by phrase, not exact punctuation/formatting.
    """
    # Find a line that contains the phrase and includes (Y/N)
    pattern = re.compile(
        rf"^(?P<line>.*{re.escape(label_phrase)}.*)\(Y/N\)(?P<rest>.*)$",
        re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        raise ValueError(f"Could not find Y/N field for label containing: {label_phrase}")

    full_line = m.group(0)
    new_line = full_line.replace("(Y/N)", f"({value})", 1)
    return text[: m.start()] + new_line + text[m.end() :]


def fill_table_practiced(text: str, table_heading: str, answers: dict[str, str]) -> str:
    """
    In the virtues table under a given heading, fill the Practiced column with Y/N.
    Assumes rows look like: | Virtue |           |
    """
    idx = text.find(table_heading)
    if idx == -1:
        raise ValueError(f"Could not find section: {table_heading}")

    after = text[idx:]
    lines = after.splitlines(True)

    # Find first table line
    table_start = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("|"):
            table_start = i
            break
    if table_start is None:
        raise ValueError(f"Could not find table after: {table_heading}")

    # Find table end
    table_end = table_start
    for j in range(table_start, len(lines)):
        if not lines[j].lstrip().startswith("|"):
            table_end = j
            break
    else:
        table_end = len(lines)

    table_lines = lines[table_start:table_end]

    def fill_row(row: str) -> str:
        m = re.match(r"^\|\s*(?P<virtue>[^|]+?)\s*\|\s*(?P<val>[^|]*)\|\s*$", row.strip())
        if not m:
            return row
        virtue = m.group("virtue").strip()
        if virtue in answers:
            return f"| {virtue} | {answers[virtue]} |\n"
        return row

    table_lines_filled = [fill_row(ln) if ln.strip().startswith("|") else ln for ln in table_lines]
    new_after = "".join(lines[:table_start] + table_lines_filled + lines[table_end:])
    return text[:idx] + new_after


def morning() -> Path:
    path = init_today(force_if_empty=True)
    text = path.read_text(encoding="utf-8")

    print("\nMorning — quick check-in\n")

    bed_on_time = ask_yn("Did you get to bed on time?")
    ended_prayer = ask_yn("Did you end the day with prayer?")
    first_alarm = ask_yn("Did you wake at the first alarm?")

    # Robust fill by label phrase (matches the template line regardless of bold/punctuation)
    text = replace_yn_for_label(text, "Did you get to bed on time", bed_on_time)
    text = replace_yn_for_label(text, "Did you end the day with prayer", ended_prayer)
    text = replace_yn_for_label(text, "Did you wake at the first alarm", first_alarm)

    print("\nVirtues (Yesterday) — y/n\n")
    virtue_answers: dict[str, str] = {}
    for v in VIRTUES:
        virtue_answers[v] = ask_yn(v)

    text = fill_table_practiced(text, "## Virtues (Yesterday) — Y/N", virtue_answers)

    path.write_text(text, encoding="utf-8")
    print(f"\n✅ Updated: {path}")
    return path


def usage() -> str:
    return (
        "Usage:\n"
        "  python tools/journal.py init\n"
        "  python tools/journal.py morning\n"
        "\n"
        "Commands:\n"
        "  init     Create today's daily entry from templates/daily.md (fills if empty)\n"
        "  morning  Ask quick Y/N prompts and fill Morning section\n"
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        print(usage())
        return 0

    cmd = argv[1].lower()

    if cmd == "init":
        path = init_today(force_if_empty=True)
        print(f"✅ Ready: {path}")
        return 0

    if cmd == "morning":
        morning()
        return 0

    print(f"Unknown command: {cmd}\n")
    print(usage())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
