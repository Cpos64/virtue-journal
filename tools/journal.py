from __future__ import annotations

import sys
from pathlib import Path
from datetime import date


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPO_ROOT / "templates" / "daily.md"
ENTRIES_ROOT = REPO_ROOT / "entries"


def today_str() -> str:
    return date.today().isoformat()  # YYYY-MM-DD


def entry_path_for(d: date) -> Path:
    yyyy = f"{d.year:04d}"
    mm = f"{d.month:02d}"
    dd = f"{d.day:02d}"
    return ENTRIES_ROOT / yyyy / mm / f"{yyyy}-{mm}-{dd}.md"


def init_today() -> Path:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    d = date.today()
    out_path = entry_path_for(d)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists():
        return out_path

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    rendered = template.replace("{{DATE}}", d.isoformat())
    out_path.write_text(rendered, encoding="utf-8")
    return out_path


def usage() -> str:
    return (
        "Usage:\n"
        "  python tools/journal.py init\n"
        "\n"
        "Commands:\n"
        "  init   Create today's daily entry from templates/daily.md\n"
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        print(usage())
        return 0

    cmd = argv[1].lower()

    if cmd == "init":
        path = init_today()
        print(f"✅ Ready: {path}")
        return 0

    print(f"Unknown command: {cmd}\n")
    print(usage())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
