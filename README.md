# Virtue Journal

A daily **Morning Check-In** and **Evening Review** journal designed to cultivate virtue,
intentional living, and faithful discipline — without friction.

**How you start and end your days plays a big role in how your days go**.

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

Definitions and intent for each virtue live in [`virtues.md`](./virtues.md).

---

## Daily Flow

### Morning Check-In (Orientation)

The morning entry sets the direction for the day.

- Review sleep and discipline from the previous night
- Reflect on **yesterday’s virtues** (Y / N)
- Set intentions:
  - What to accomplish
  - How to learn and grow
  - How to give
- Begin the day with prayer and the Word

This is designed to be **quick, honest, and grounding**.

Run with:
```bash
python tools/journal.py morning
```

---

### Evening Review (Reflection + Pre-Decision)

The evening entry closes the day intentionally and prepares for tomorrow.

- Review the day honestly
- Reflect on learning and gratitude
- Evaluate **today’s virtues** (Y / N)
- Pre-decide:
  - bedtime
  - prayer before sleep
  - one action to set tomorrow up well

Tomorrow begins with how today ends.

Run with:
```bash
python tools/journal.py evening
```

---

## How to Use

### Create today’s entry
Creates the daily markdown file if it doesn’t exist.

```bash
python tools/journal.py init

