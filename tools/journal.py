from __future__ import annotations

import sys
import re
from pathlib import Path
from datetime import date, timedelta

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
    "Generosity",
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

    def build_today_text() -> str:
        text = render_daily_template(d)
        unfinished = get_unfinished_tasks()
        if unfinished:
            text = replace_bullets_under_question(
                text,
                "What do you want to accomplish?",
                unfinished,
            )
        return text

    if out_path.exists():
        if force_if_empty:
            existing = out_path.read_text(encoding="utf-8", errors="ignore")
            if existing.strip() == "":
                out_path.write_text(build_today_text(), encoding="utf-8")
        return out_path

    out_path.write_text(build_today_text(), encoding="utf-8")
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


def ask_text(prompt: str) -> str:
    """Return a single-line text answer (can be blank)."""
    return input(f"{prompt}: ").rstrip()


def ask_multi_items(prompt: str) -> list[str]:
    items: list[str] = []
    while True:
        ans = ask_text(f"{prompt} (d if done)").strip()
        if ans.lower() in {"d", "done"}:
            break
        if ans:
            items.append(ans)
    return items


def replace_yn_for_label(text: str, label_phrase: str, value: str) -> str:
    """
    Replace the first '(...)' Y/N marker on a line containing label_phrase with '(Y)' or '(N)'.

    Works whether the line currently contains:
      (Y/N)  OR  (Y)  OR  (N)

    This makes the CLI safe to run multiple times.
    """
    # Match a line containing the phrase and a parenthesized marker (Y/N, Y, or N)
    pattern = re.compile(
        rf"^(?P<line>.*{re.escape(label_phrase)}.*)\((Y/N|Y|N)\)(?P<rest>.*)$",
        re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        raise ValueError(f"Could not find Y/N field for label containing: {label_phrase}")

    full_line = m.group(0)
    # Replace only the first occurrence of the marker on that line
    new_line = re.sub(r"\((Y/N|Y|N)\)", f"({value})", full_line, count=1)
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


def remove_empty_bullets(text: str) -> str:
    """
    Remove markdown list items that are just '- ' or '-'.
    """
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if line.strip() in {"-", "- "}:
            continue
        cleaned.append(line)
    return "\n".join(cleaned) + "\n"

def replace_bullets_under_question(text: str, question_phrase: str, items: list[str]) -> str:
    """
    Find the line containing `question_phrase`, then replace the markdown bullet list
    immediately below it with `items` formatted as "- ...".

    Stops replacing when it hits a non-bullet line.
    """
    lines = text.splitlines(True)

    for i, line in enumerate(lines):
        if question_phrase in line:
            j = i + 1

            # Skip and remove existing bullet lines under the question
            while j < len(lines) and lines[j].lstrip().startswith("-"):
                j += 1

            bullet_lines = [f"- {it}\n" for it in items]
            new_lines = lines[: i + 1] + bullet_lines + lines[j:]
            return "".join(new_lines)

    raise ValueError(f"Could not find question line containing: {question_phrase}")


def replace_single_bullet_under_question(text: str, question_phrase: str, value: str) -> str:
    value = value.strip()
    if not value:
        return text
    return replace_bullets_under_question(text, question_phrase, [value])

def get_unfinished_tasks() -> list[str]:
    yesterday = date.today() - timedelta(days=1)
    yesterday_file = entry_path_for(yesterday)

    unfinished: list[str] = []

    if not yesterday_file.exists():
        return unfinished

    text = yesterday_file.read_text(encoding="utf-8")

    pattern = r"\*\*Accomplishments \(from this morning\):\*\*([\s\S]*?)(?:\n##|\Z)"
    match = re.search(pattern, text)

    if not match:
        return unfinished

    for line in match.group(1).splitlines():
        line = line.strip()
        if line.startswith("- [N]"):
            task = line.replace("- [N]", "", 1).strip()
            if task:
                unfinished.append(task)

    return unfinished

def morning() -> Path:
    path = init_today(force_if_empty=True)
    text = path.read_text(encoding="utf-8")

    print("\nMorning — quick check-in\n")

    time_in_bed = ask_text("Time in bed (e.g., 10:30 PM - 6:15 AM)")
    hours_slept = ask_text("Hours slept (e.g., 7h45m)")

    bed_on_time = ask_yn("Did you get to bed on time?")
    ended_prayer = ask_yn("Did you end the day with prayer?")
    first_alarm = ask_yn("Did you wake at the first alarm?")

    # Fill Sleep & Discipline fields
    if time_in_bed.strip():
        text = replace_line_value(text, "Time in bed:", time_in_bed.strip())
    if hours_slept.strip():
        text = replace_line_value(text, "Hours slept:", hours_slept.strip())

    # Fill Y/N fields (robust by label phrase)
    text = replace_yn_for_label(text, "Did you get to bed on time", bed_on_time)
    text = replace_yn_for_label(text, "Did you end the day with prayer", ended_prayer)
    text = replace_yn_for_label(text, "Did you wake at the first alarm", first_alarm)


    print("\nVirtues (Yesterday) — y/n\n")
    virtue_answers: dict[str, str] = {}
    for v in VIRTUES:
        virtue_answers[v] = ask_yn(v)

    text = fill_table_practiced(text, "## Virtues (Yesterday) — Y/N", virtue_answers)

    # Accomplishments (multi-item loop)
    existing_accomplishments = read_bullets_under_question(text, "What do you want to accomplish?")
    new_accomplishments = ask_multi_items("What do you want to accomplish?")

    combined_accomplishments = existing_accomplishments.copy()
    for item in new_accomplishments:
        if item not in combined_accomplishments:
            combined_accomplishments.append(item)

    if combined_accomplishments:
        text = replace_bullets_under_question(
            text,
            "What do you want to accomplish?",
            combined_accomplishments,
        )

    # Learning & Giving (single-item)
    learn_grow = ask_text("How will you learn and grow?")
    give_today = ask_text("How will you give?")

    scripture_read = ask_text("Scripture read (e.g., Matthew 5)")
    prayer_focus = ask_text("Prayer focus")

    text = replace_single_bullet_under_question(text, "How will you learn and grow?", learn_grow)
    text = replace_single_bullet_under_question(text, "How will you give?", give_today)

    if scripture_read.strip():
        text = replace_line_value(text, "Scripture read:", scripture_read.strip())
    if prayer_focus.strip():
        text = replace_line_value(text, "Prayer focus:", prayer_focus.strip())


    text = remove_empty_bullets(text)
    path.write_text(text, encoding="utf-8")
    print(f"\n✅ Updated: {path}")
    return path


def replace_line_value(text: str, line_prefix: str, value: str) -> str:
    """
    Replace the value on a markdown bullet line that starts with line_prefix.

    Example:
      - **What time will you get into bed?** 9:15 PM

    Re-running will replace the existing value (9:15 PM) with the new one.
    """
    # Match the full line that contains the label (the bold text), and capture it up to the closing **
    pattern = re.compile(
        rf"^(?P<label>\s*-\s*\*\*{re.escape(line_prefix)}\*\*)(?P<after>.*)$",
        re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        raise ValueError(f"Could not find line for: {line_prefix}")

    # Replace entire trailing part with exactly one space + value (or nothing if value blank)
    new_line = f"{m.group('label')} {value}".rstrip()
    return text[: m.start()] + new_line + text[m.end() :]

def read_bullets_under_question(text: str, question_phrase: str) -> list[str]:
    """
    Read markdown bullet items (lines starting with '-') immediately under the line
    containing `question_phrase`. Stops when a non-bullet line is reached.
    Returns the bullet text without the leading '- '.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if question_phrase in line:
            items: list[str] = []
            j = i + 1
            while j < len(lines):
                ln = lines[j].strip()
                if not ln.startswith("-"):
                    break
                item = ln.lstrip("-").strip()
                if item:
                    items.append(item)
                j += 1
            return items
    return []


def evening() -> Path:
    path = init_today(force_if_empty=True)
    text = path.read_text(encoding="utf-8")

    print("\nEvening — quick review & pre-decision\n")

    # 1) Per-accomplishment accountability (from morning bullets)
    accomplishments = read_bullets_under_question(text, "What do you want to accomplish?")
    accomplished_results: list[str] = []

    if accomplishments:
        print("\nAccomplishments — y/n\n")
        for item in accomplishments:
            yn = ask_yn(f"Did you: {item}")
            accomplished_results.append(f"[{yn}] {item}")
    else:
        print("\n(No accomplishments listed this morning.)\n")

    # 2) Other evening prompts
    learned = ask_text("What did you learn?")
    goodness = ask_text("How did you see the Father’s goodness?")

    will_pray = ask_yn("Will you pray before sleep?")
    bedtime = ask_text("What time will you get into bed (e.g., 10:30 PM)")
    one_thing = ask_text("One thing you'll do to set tomorrow up well")

    # 3) Write accomplishments into the Evening Review section
    if accomplished_results:
        text = replace_bullets_under_question(
            text,
            "Accomplishments (from this morning):",
            accomplished_results,
        )


    # 4) Fill the other evening bullets
    text = replace_single_bullet_under_question(text, "What did you learn?", learned)
    text = replace_single_bullet_under_question(text, "How did you see the Father’s goodness?", goodness)

    # 5) Fill Pre-Decision (Tonight) fields
    text = replace_yn_for_label(text, "Will you pray before sleep", will_pray)

    if bedtime.strip():
        text = replace_line_value(text, "What time will you get into bed?", bedtime.strip())
    if one_thing.strip():
        text = replace_bullets_under_question(
            text,
            "What is one thing you’ll do to set tomorrow up well?",
            [one_thing.strip()],
        )

    text = remove_empty_bullets(text)
    path.write_text(text, encoding="utf-8")
    print(f"\n✅ Updated: {path}")
    return path



def usage() -> str:
    return (
        "Usage:\n"
        "  python tools/journal.py init\n"
        "  python tools/journal.py morning\n"
        "  python tools/journal.py evening\n"
        "\n"
        "Commands:\n"
        "  init     Create today's daily entry from templates/daily.md (fills if empty)\n"
        "  morning  Ask quick Y/N prompts and fill Morning section\n"
        "  evening  Ask quick prompts and fill Evening section\n"
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
    
    if cmd == "evening":
        evening()
        return 0


    print(f"Unknown command: {cmd}\n")
    print(usage())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
