# GitHub Actions for Testers — 1-Hour Workshop Design

**Date:** 2026-07-27
**Session date:** 2026-07-30
**Audience:** Manual testers and aspiring test automation engineers (beginners to CI/CD). The facilitator is also learning.
**Format:** Facilitator drives, room watches. Attendees get the repo link to explore later.
**Duration:** 60 minutes.

## 1. Goal

By the end of the hour, every attendee (and the facilitator) can answer:

1. **What is GitHub Actions / CI?** — a robot that runs your tests automatically when code changes.
2. **Where is it configured?** — YAML files in the `.github/workflows/` folder of a repo; GitHub auto-detects them.
3. **How is it triggered?** — the `on:` block: `push`, `pull_request`, `workflow_dispatch` (manual button), and `schedule` (nightly).
4. **How do I write the YAML?** — treat it as a fill-in-the-blank form: `name / on / jobs / runs-on / steps`; indentation is the one rule that bites.

The emotional hook is the **red → green feedback loop**: watch a test fail in CI (red ✗), fix it, watch it pass (green ✓).

## 2. Pedagogical framing

Story-driven ("Red → Green feedback loop"), not syntax-driven. CI is taught through the one thing testers already care about — pass/fail feedback — with the PR-gate moment (a failing check blocking a merge) as the emotional peak. YAML anatomy is taught once, live, then reinforced by revealing later stages.

**Out of scope (mention verbally only):** branch-protection rule setup, secrets, and deployment. Not covered because they add clicks/concepts that don't fit a 60-minute testing intro.

## 3. The sample repository

A tiny pure-Python cart/price calculator with pytest tests. Chosen because it stays green in seconds, needs zero external setup, and every tester understands "add item, total, apply discount." It is trivial to break on purpose for the red→green moment.

```
gha-for-testers/
├── src/cart.py            # ~4 tiny functions: add_item, total, apply_discount, ...
├── tests/test_cart.py     # pytest tests — includes one we deliberately break live
├── requirements.txt       # just pytest
├── README.md              # short intro + mental-model diagram + status badge (added at Stage 4)
├── facilitator.html       # the scripted presenter view (open in a browser, read from screen)
├── CHEATSHEET.md          # one-page handout
├── stages/                # reference copies of each stage's final YAML (facilitator safety net)
│   ├── v1-push.yml
│   ├── v2-triggers.yml
│   ├── v3-matrix.yml
│   └── v4-badge-artifact.yml
└── .github/workflows/
    └── tests.yml          # the ONE active workflow, evolved live across the session
```

The live workflow is a single `.github/workflows/tests.yml` that evolves through the session. The top-level `stages/` folder holds a known-good copy of each stage's final YAML so the facilitator can copy-paste to recover instantly if a live edit goes wrong. **These reference copies live OUTSIDE `.github/workflows/` on purpose** — GitHub runs every triggered `.yml` inside `.github/workflows/`, so keeping the stage copies elsewhere ensures `tests.yml` stays the only workflow that actually runs during the session.

## 4. The four workflow stages

Each stage maps to one learning objective. **Stage 1 is typed live from a blank file in GitHub's Actions tab** ("set up a workflow yourself"); Stages 2–4 are revealed from pre-written reference and applied as diffs to `tests.yml`.

| Stage | Change to `tests.yml` | New concept | Trigger taught | The "aha" |
|---|---|---|---|---|
| **1** (live build) | Create from blank | YAML anatomy: `name / on / jobs / runs-on / steps` | `on: push` | Commit → Actions tab → first green ✓ |
| **2** | Edit | Triggers + the PR gate | add `pull_request` + `workflow_dispatch` | Break a test → open PR → red ✗ blocks merge; click **Run workflow** to show manual trigger |
| **3** | Edit | Test many versions at once | (same) | `strategy: matrix` runs Python 3.10 / 3.11 / 3.12 in parallel |
| **4** | Edit | Proof & reporting | mention `schedule:` (nightly) | Green **status badge** in README + pytest report uploaded as a downloadable **artifact** |

### Stage 1 YAML (typed live)
The canonical anatomy the facilitator types from blank:
```yaml
name: Tests
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest
```

### Stage 2 adds
```yaml
on:
  push:
  pull_request:
  workflow_dispatch:
```

### Stage 3 adds
```yaml
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    ...
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### Stage 4 adds
Status badge line in README, `pytest --junitxml=report.xml`, and an `actions/upload-artifact@v4` step; `schedule:` shown in the run-sheet but only mentioned verbally.

## 5. The 60-minute shape

- **0–8** — What/why: CI in one sentence + mental-model diagram (event → workflow → job → step → runner) + where config lives (`.github/workflows/`).
- **8–25** — Stage 1: live-build the YAML from blank in the Actions tab → commit → first green run. The YAML-as-fill-in-a-form lesson.
- **25–38** — Stage 2: triggers (`pull_request`, manual `workflow_dispatch`) + the red→green PR gate (emotional peak).
- **38–48** — Stage 3: matrix across Python versions.
- **48–54** — Stage 4: badge + artifact.
- **54–60** — Recap against the 4 objectives + hand out cheat-sheet + Q&A.

## 6. Facilitator materials

### `facilitator.html` — fully-scripted visual presenter view
A single self-contained HTML file (inline CSS/JS, no internet needed) the facilitator **opens in a browser and reads straight off the screen**. It must never require searching for words or remembering the next step — everything is on screen, in order, visually unmistakable. It is the primary teaching material; there is no separate markdown run-sheet.

**Layout — every step is one "card", and every card has the same three colour-coded zones so the eye always knows where to look:**

| Zone | Label & colour | Contents |
|---|---|---|
| 🗣️ **TALK** | "Say this" (blue) | The exact words to read aloud, verbatim — including the transition line into the step and the question to pose to the room. Big, high-contrast, read-aloud type size. |
| 🖱️ **DO** | "Do this" (amber) | The precise clicks/navigation named literally (e.g. "Click the **Actions** tab → **Configure** → green **Commit changes** button") plus any exact text/YAML to type, in a copy-button code block. |
| 📺 **SHOW** | "Show them" (green) | How to demonstrate progress: what to point at and the exact words to narrate while it happens ("yellow dot = running… now a green tick = pass"), plus the one-sentence **aha** to say out loud. |

**Showing "where it lives":**
- The intro (0–8 min) includes a **file-tree visual baked into the card** — the repo structure with `.github/workflows/tests.yml` highlighted — so the facilitator can point at exactly where a workflow lives before ever opening GitHub. The cheat-sheet carries the same tree.
- Right after the first commit, a dedicated **"show them the folder" step**: navigate the GitHub repo file browser into `.github` → `workflows`, click `tests.yml`, and narrate "this is the whole configuration — it's just this one file, in this one folder." This makes objective #2 (where config lives) concrete on screen, not just spoken.

**Structure and navigation:**
- Cards are ordered exactly as the 60-minute run (§5); each card shows its **stage number and a running clock target** (e.g. "Stage 2 · aim to be here by 0:25") so the facilitator can pace themselves at a glance.
- A slim **progress rail / step list** down the side (or top) to jump between cards; big Next/Prev controls or arrow-key navigation so it works like a teleprompter.
- The complete Stage 1 YAML to type and the precise one-line test edit that turns the suite **red** — plus the exact edit that turns it **green** again — each in its own card with its own TALK script and a copy button.
- A **glossary strip** (how to say "runner", "job", "workflow" in plain words) pinned where it's always visible, so terminology stays consistent.
- A **"Dry-run for yourself first"** card at the top: an ordered, checkbox list (state saved in the browser) so the facilitator can execute the whole session solo end-to-end — reading the same script to themselves — and tick off each confirmed step before 2026-07-30.
- A **"if wifi / Actions is slow" fallback** card: embedded screenshots of each green/red run + pointer to the `stages/` reference files, with a TALK line to cover the pause.
- Print-friendly CSS so it can also be printed as a paper script if preferred.

### `CHEATSHEET.md` — one-page handout
- Mental-model diagram (event → workflow → job → step → runner).
- Annotated YAML skeleton.
- The 4 triggers (`push`, `pull_request`, `workflow_dispatch`, `schedule`).
- "Indentation is the #1 gotcha" callout.

## 7. Success criteria

- The facilitator can run the entire session by reading `facilitator.html` aloud verbatim, without improvising wording or hunting for the next step — talk / do / show is unmistakable on every card.
- The facilitator can complete a full solo dry-run using only `facilitator.html`, watching real green and red runs in their own GitHub repo, and ticking off every step, before 2026-07-30.
- During the session, the room sees at least one live green run, one red run, and one red→green recovery.
- Each of the 4 learning objectives (§1) is explicitly hit and recapped.
- The whole demo fits in 60 minutes with a working fallback if the network fails.

## 8. Prerequisites

- The facilitator has a GitHub account and a repo (public) they can push to and screen-share.
- Python 3.12 locally to verify `pytest` is green before pushing (optional but recommended for the dry-run).
- Nothing installed on attendees' machines — they only watch.
