# Virtue Journal

A daily **Morning Check-In** and **Evening Review** journal designed to cultivate virtue,
intentional living, and faithful discipline — without friction.

**"How you begin and conclude each day shapes the day itself."**

---

## Core Ideas

- **Virtue over metrics** — character formation, not gamification
- **Binary accountability** where possible (Y / N)
- **Reflection without rumination**
- **Faith-centered rhythms** (prayer, Scripture, gratitude)
- **Markdown-first** — readable now, readable decades from now

---

## Virtues Tracked

The following virtues are evaluated daily using a simple **Y / N** reflection:

- Silence
- Frugality
- Industry
- Humility
- Mindfulness
- Contentment
- Abstinence
- Purity
- Wisdom
- Moderation
- Generosity

Definitions and intent for each virtue live in [`virtues.md`](./virtues.md).

---

## Daily Flow

### Morning Check-In (Orientation)

The morning entry sets the direction for the day.

- Review sleep and discipline from the previous night
- Reflect on **yesterday’s virtues** (Y / N)
- Review unfinished items from yesterday and choose (Y/N) whether to carry each one into today
- Set intentions:
  - What to accomplish
  - What are your plans after work
- Begin the day with prayer and the Word

This is designed to be **quick, honest, and grounding**.

---

### Evening Review (Reflection + Pre-Decision)

The evening entry closes the day intentionally and prepares for tomorrow.

- Review accomplishments from this morning (each item is checked **Y/N**)
- Reflect on learning and gratitude
- Pre-decide:
  - bedtime
  - prayer before sleep
  - one action to set tomorrow up well

Tomorrow begins with how today ends.

---

### Weekly Planning (Sunday)

On Sundays, the daily entry includes a **Weekly Plan (Mon-Sat)** section so you can map out
Monday through Saturday.

- Fill in weekly plans on Sunday
- Monday-Saturday entries automatically carry those weekly plan lines forward
- The next Sunday plan becomes the new source for the upcoming week

This keeps your week visible each day without extra prompts.

---

## How to Use

### Create today’s entry
1) Create the daily markdown file if it doesn’t exist. 

Run with:
```bash
python tools/journal.py init
```

2) Launch Morning Check-In (CLI)

Run with:
```bash
python tools/journal.py morning
```

3) Launch Evening Review (CLI)

Run with:
```bash
python tools/journal.py evening
```

> Note: journal entries live locally in `entries/` and are ignored by Git (via `.gitignore`).