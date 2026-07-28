# GitHub Actions for Testers — Workshop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained teaching repo that lets one facilitator run a spoon-fed, 60-minute "GitHub Actions for testers" session (and dry-run it solo first).

**Architecture:** A tiny pure-Python cart library with pytest is the thing being automated. Four progressive workflow files (reference copies, kept inert in a `stages/` subfolder GitHub ignores) show the CI story growing. A single self-contained `facilitator.html` is the scripted presenter (TALK/DO/SHOW cards + nav + checklist), backed by a one-page `CHEATSHEET.md` and a `README.md`.

**Tech Stack:** Python 3.12 (runs on 3.10–3.12 in CI), pytest, GitHub Actions YAML, plain HTML/CSS/vanilla JS (no build, no dependencies, no internet needed to open).

## Global Constraints

- Spec of record: `docs/superpowers/specs/2026-07-27-github-actions-workshop-design.md`. Every task implements part of it.
- Session date 2026-07-30; the facilitator must be able to complete a full solo dry-run before then using only `facilitator.html`.
- `facilitator.html` is a single file: all CSS/JS inline, works offline, opens by double-click. No external fetches, no `position: fixed`.
- Governing content principle: **spoon-fed, zero assumed knowledge** — every click and button label named; auto-behaviors (e.g. GitHub creating the `.github/workflows` folder on commit) stated explicitly.
- Reference workflows live in `.github/workflows/stages/` (a subfolder). GitHub Actions only runs `*.yml` at the top level of `.github/workflows/`, so subfolder files never run — this is why they are safe to ship. The top-level `tests.yml` is intentionally NOT shipped; the facilitator builds it live during the session.
- Commit messages: no `Co-Authored-By` / Claude attribution trailers.
- No new Python dependency beyond `pytest`.
- Sentence-case copy; no emoji inside code. (Zone-label emoji in `facilitator.html` UI are allowed as they are content, not code.)

---

### Task 1: Sample Python cart library + pytest suite

**Files:**
- Create: `src/cart.py`
- Create: `tests/test_cart.py`
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `.gitignore`

**Interfaces:**
- Produces: `add_item(cart: list, name: str, price: float, quantity: int = 1) -> list`, `total(cart: list) -> float`, `apply_discount(amount: float, percent: float) -> float`. Consumed by the tests and by every workflow's `pytest` step. The live "break" in the session edits `src/cart.py:apply_discount` (see facilitator card, Task 4).

- [ ] **Step 1: Create `pytest.ini` so tests can import from `src/`**

```ini
[pytest]
pythonpath = src
```

- [ ] **Step 2: Create `requirements.txt`**

```
pytest
```

- [ ] **Step 3: Create `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
report.xml
```

- [ ] **Step 4: Write the failing tests**

Create `tests/test_cart.py`:

```python
from cart import add_item, total, apply_discount


def test_add_item_adds_one_row():
    cart = add_item([], "apple", 0.50)
    assert cart == [{"name": "apple", "price": 0.50, "quantity": 1}]


def test_total_multiplies_price_by_quantity():
    cart = add_item(add_item([], "apple", 0.50, 2), "bread", 1.20)
    assert total(cart) == 2.20


def test_apply_discount_takes_percent_off():
    assert apply_discount(100.0, 10) == 90.0
```

- [ ] **Step 5: Run tests to verify they fail**

Run: `pytest -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'cart'` (implementation not written yet).

- [ ] **Step 6: Write the minimal implementation**

Create `src/cart.py`:

```python
def add_item(cart, name, price, quantity=1):
    return cart + [{"name": name, "price": price, "quantity": quantity}]


def total(cart):
    return sum(item["price"] * item["quantity"] for item in cart)


def apply_discount(amount, percent):
    return round(amount * (1 - percent / 100), 2)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `pytest -v`
Expected: PASS — 3 passed.

- [ ] **Step 8: Commit**

```bash
git add src/cart.py tests/test_cart.py requirements.txt pytest.ini .gitignore
git commit -m "Add cart library and pytest suite for the workshop sample"
```

---

### Task 2: Four progressive workflow reference files

**Files:**
- Create: `.github/workflows/stages/v1-push.yml`
- Create: `.github/workflows/stages/v2-triggers.yml`
- Create: `.github/workflows/stages/v3-matrix.yml`
- Create: `.github/workflows/stages/v4-badge-artifact.yml`

**Interfaces:**
- Consumes: `requirements.txt` and `pytest` from Task 1 (the `pip install` + `pytest` steps).
- Produces: the exact YAML the facilitator types (v1) or reveals (v2–v4) during the session, and the safety-net copies referenced by the wifi-fallback card. `v4` is the final shape the top-level `tests.yml` reaches by end of session.

- [ ] **Step 1: Create `v1-push.yml` (Stage 1 — the live-typed anatomy)**

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

- [ ] **Step 2: Create `v2-triggers.yml` (Stage 2 — adds PR + manual triggers)**

```yaml
name: Tests
on:
  push:
  pull_request:
  workflow_dispatch:
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

- [ ] **Step 3: Create `v3-matrix.yml` (Stage 3 — many Python versions at once)**

```yaml
name: Tests
on:
  push:
  pull_request:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest
```

- [ ] **Step 4: Create `v4-badge-artifact.yml` (Stage 4 — report + downloadable artifact)**

Note the artifact name includes `${{ matrix.python-version }}`: `actions/upload-artifact@v4` rejects duplicate artifact names across matrix jobs, so each job needs a unique name. `if: always()` uploads the report even when tests fail (that is when a report matters most).

```yaml
name: Tests
on:
  push:
  pull_request:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest --junitxml=report.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-report-${{ matrix.python-version }}
          path: report.xml
```

- [ ] **Step 5: Verify the files exist, are in the inert subfolder, and carry the key markers**

Run:
```bash
ls .github/workflows/*.yml 2>/dev/null && echo "PROBLEM: a top-level workflow exists" || echo "OK: no top-level workflow (correct)"
grep -l "runs-on: ubuntu-latest" .github/workflows/stages/v*.yml | wc -l
grep -q "matrix:" .github/workflows/stages/v3-matrix.yml && echo "v3 has matrix OK"
grep -q "upload-artifact@v4" .github/workflows/stages/v4-badge-artifact.yml && echo "v4 has artifact OK"
grep -q "workflow_dispatch:" .github/workflows/stages/v2-triggers.yml && echo "v2 has manual trigger OK"
```
Expected: "OK: no top-level workflow (correct)", then `4`, then the three "OK" lines.

- [ ] **Step 6: Optional deeper YAML lint (only if PyYAML is present)**

Run:
```bash
python3 -c "import yaml" 2>/dev/null && python3 -c "import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/stages/v*.yml')]; print('YAML parses OK')" || echo "PyYAML not installed — skipping (grep checks in Step 5 are sufficient)"
```
Expected: "YAML parses OK" or the skip message.

- [ ] **Step 7: Commit**

```bash
git add .github/workflows/stages/
git commit -m "Add four progressive workflow reference files (inert stages copies)"
```

---

### Task 3: README and one-page cheat-sheet

**Files:**
- Create: `README.md`
- Create: `CHEATSHEET.md`

**Interfaces:**
- Consumes: the mental model (event → workflow → job → step → runner) and the file-tree, both reused verbatim in `facilitator.html` (Task 4) so terminology stays identical.
- Produces: the badge markdown with a clearly-marked placeholder the facilitator replaces with their own `owner/repo`.

- [ ] **Step 1: Create `README.md`**

The badge line uses placeholders in ALL CAPS so it is obvious what to replace. Until the facilitator builds `tests.yml` live and pushes, the badge shows "no status" — that is expected and is itself a teachable "the robot hasn't run yet" moment.

```markdown
# GitHub Actions for Testers — sample project

<!-- After you create tests.yml live and push, replace OWNER/REPO below with your GitHub username and repo name. -->
![Tests](https://github.com/OWNER/REPO/actions/workflows/tests.yml/badge.svg)

A tiny cart/price calculator with pytest tests. We use it to learn GitHub Actions:
a robot that runs your tests automatically whenever code changes.

## The mental model

    event  →  workflow  →  job  →  step  →  runner

- **event** — something happens (a push, a pull request, a click).
- **workflow** — a `.yml` file in `.github/workflows/` that says what to do.
- **job** — a batch of steps that run together on one machine.
- **step** — a single command or action.
- **runner** — the machine GitHub gives you to run the job on.

## Run the tests yourself

    pip install -r requirements.txt
    pytest

## Where the automation lives

    .github/
      workflows/
        tests.yml   ← the whole configuration is this one file

`.github/workflows/stages/` holds reference copies of each stage (v1–v4). They sit
in a subfolder on purpose: GitHub only runs `.yml` files at the top level of
`.github/workflows/`, so these copies never run — they are just safety-net examples.
```

- [ ] **Step 2: Create `CHEATSHEET.md` (the one-page handout)**

```markdown
# GitHub Actions cheat-sheet

## Mental model
event → workflow → job → step → runner

## Where it lives
    .github/workflows/tests.yml
GitHub only reads `.yml` files at the TOP level of `.github/workflows/`.
You do not create the folder by hand — GitHub makes it when you commit.

## The YAML skeleton (fill in the blanks)
    name: Tests              # any label you like
    on: push                 # WHEN it runs
    jobs:
      test:                  # a job (pick any name)
        runs-on: ubuntu-latest   # WHICH machine
        steps:               # WHAT to do, in order
          - uses: actions/checkout@v4          # get the code
          - uses: actions/setup-python@v5      # install python
            with:
              python-version: "3.12"
          - run: pip install -r requirements.txt
          - run: pytest

## The 4 triggers you'll meet
- push               — runs on every push
- pull_request       — runs on PRs (this is what blocks a bad merge)
- workflow_dispatch  — adds a manual "Run workflow" button
- schedule           — runs on a timer (e.g. nightly)

## #1 gotcha
Indentation matters. Use spaces, never tabs. Line things up exactly.
```

- [ ] **Step 3: Verify required content is present**

Run:
```bash
grep -q "OWNER/REPO" README.md && echo "badge placeholder OK"
grep -q "event → workflow → job → step → runner" CHEATSHEET.md && echo "mental model OK"
grep -q "workflow_dispatch" CHEATSHEET.md && echo "triggers OK"
```
Expected: three "OK" lines.

- [ ] **Step 4: Commit**

```bash
git add README.md CHEATSHEET.md
git commit -m "Add README and one-page cheat-sheet"
```

---

### Task 4: The scripted presenter — `facilitator.html`

**Files:**
- Create: `facilitator.html`

**Interfaces:**
- Consumes: the cart function names and the exact break edit from Task 1; the four workflow YAMLs from Task 2 (Stage 1 YAML is typed live, so its text appears here verbatim); the mental model + file-tree from Task 3.
- Produces: the primary teaching artifact. Nine ordered cards + a top dry-run checklist, a pinned glossary, and a wifi-fallback card. Teleprompter nav (Prev/Next + arrow keys), checklist state saved via `localStorage`, print-friendly.

**Card order (matches spec §5 timing):**
0. Dry-run checklist (top, untimed) · 1. What is CI + file-tree (0–8) · 2. Stage 1 build live (8–25) · 3. Show the folder on GitHub · 4. First green run · 5. Stage 2 triggers + PR gate, red→green (25–38) · 6. Stage 3 matrix (38–48) · 7. Stage 4 badge + artifact (48–54) · 8. Recap + Q&A (54–60). Plus a fixed glossary strip and a fallback card.

**Zone rule for every timed card:** three colour-coded blocks — 🗣️ SAY THIS (blue `#378ADD`), 🖱️ DO THIS (amber `#EF9F27`), 📺 SHOW THEM (green `#639922`), with the one-line *aha* pinned under SHOW. Each SAY block is the largest, read-aloud type. Each code/YAML block has a Copy button.

**Red→green break (used on Card 5):** to go RED, edit `src/cart.py` line `return round(amount * (1 - percent / 100), 2)` to `return round(amount, 2)` (forgets the discount) — the existing `test_apply_discount_takes_percent_off` catches it. To go GREEN, revert that one line. This realises spec §6's red→green step as a real one-line bug the tests catch (the strongest story for testers).

- [ ] **Step 1: Create `facilitator.html` with the full skeleton (styles + nav + checklist JS)**

Create `facilitator.html`:

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Facilitator — GitHub Actions for testers</title>
<style>
  :root { --blue:#378ADD; --amber:#EF9F27; --green:#639922; --ink:#1a1a1a; --muted:#666; --line:#ddd; --bg:#fafafa; }
  * { box-sizing: border-box; }
  body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; color: var(--ink); background: var(--bg); margin: 0; line-height: 1.6; }
  .wrap { max-width: 860px; margin: 0 auto; padding: 16px; }
  .glossary { position: sticky; top: 0; z-index: 5; background: #fff; border-bottom: 1px solid var(--line); padding: 8px 16px; font-size: 13px; color: var(--muted); }
  .glossary b { color: var(--ink); font-weight: 600; }
  .card { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 18px; margin: 16px 0; display: none; }
  .card.active { display: block; }
  .card.checklist, .card.fallback { display: block; }
  .head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
  .stage { background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 3px 9px; font-size: 13px; }
  .clock { font-size: 13px; color: var(--muted); }
  .zone { border-left: 4px solid var(--line); border-radius: 0; padding: 10px 14px; margin: 10px 0; background: #fff; }
  .zone .label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 6px; }
  .say { border-left-color: var(--blue); background: #f2f8fe; }
  .say .label { color: var(--blue); }
  .say p { font-size: 20px; margin: 0; }
  .do { border-left-color: var(--amber); background: #fef8ef; }
  .do .label { color: #a5670c; }
  .show { border-left-color: var(--green); background: #f3f8ea; }
  .show .label { color: #4c7515; }
  .aha { display: inline-block; margin-top: 8px; background: #e7f3d8; color: #3b5c12; border-radius: 8px; padding: 5px 10px; font-size: 15px; }
  pre { position: relative; background: #f6f6f4; border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; overflow-x: auto; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 13px; line-height: 1.7; }
  .copy { position: absolute; top: 8px; right: 8px; font: inherit; font-size: 12px; padding: 3px 8px; border: 1px solid var(--line); border-radius: 6px; background: #fff; cursor: pointer; }
  .tree { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 14px; line-height: 1.9; }
  .tree .hi { background: #e7f3d8; color: #3b5c12; border-radius: 6px; padding: 1px 8px; }
  .nav { display: flex; justify-content: space-between; gap: 8px; margin-top: 14px; }
  .nav button, .rail button { font: inherit; padding: 8px 12px; border: 1px solid var(--line); border-radius: 8px; background: #fff; cursor: pointer; }
  .rail { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 4px; }
  .rail button.here { border-color: var(--blue); color: var(--blue); font-weight: 600; }
  .checklist li { margin: 6px 0; }
  .fallback { border-color: var(--amber); }
  .runrow { display: flex; align-items: center; gap: 8px; border: 1px solid var(--line); border-radius: 8px; padding: 8px 12px; margin: 6px 0; font-size: 14px; }
  .dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
  .dot.green { background: #2da44e; } .dot.red { background: #cf222e; }
  @media print { .card { display: block !important; } .nav, .rail { display: none; } }
</style>
</head>
<body>
<div class="glossary">
  Plain words: <b>runner</b> = the computer GitHub lends you · <b>job</b> = a batch of steps on one runner · <b>workflow</b> = the whole .yml file · <b>step</b> = one command · <b>event</b> = the thing that starts it.
</div>
<div class="wrap">
  <div class="rail" id="rail"></div>

  <!-- CARDS GET INSERTED HERE IN STEPS 2–4 -->

  <div class="nav">
    <button id="prev">← Prev</button>
    <button id="next">Next →</button>
  </div>
</div>
<script>
  function copyBtn(pre){ const b=document.createElement('button'); b.className='copy'; b.textContent='Copy';
    b.onclick=()=>{ const t=pre.cloneNode(true); const x=t.querySelector('.copy'); if(x)x.remove();
    navigator.clipboard.writeText(t.textContent.trim()); b.textContent='Copied'; setTimeout(()=>b.textContent='Copy',1200); };
    pre.appendChild(b); }
  document.querySelectorAll('pre').forEach(copyBtn);

  const cards=[...document.querySelectorAll('.card.step')];
  const rail=document.getElementById('rail');
  let i=0;
  cards.forEach((c,n)=>{ const b=document.createElement('button'); b.textContent=(c.dataset.short||('#'+n));
    b.onclick=()=>go(n); rail.appendChild(b); });
  function go(n){ i=Math.max(0,Math.min(cards.length-1,n));
    cards.forEach((c,k)=>c.classList.toggle('active',k===i));
    [...rail.children].forEach((b,k)=>b.classList.toggle('here',k===i));
    window.scrollTo({top:0,behavior:'smooth'}); }
  document.getElementById('prev').onclick=()=>go(i-1);
  document.getElementById('next').onclick=()=>go(i+1);
  document.addEventListener('keydown',e=>{ if(e.key==='ArrowRight')go(i+1); if(e.key==='ArrowLeft')go(i-1); });

  document.querySelectorAll('input[type=checkbox][data-k]').forEach(cb=>{
    cb.checked=localStorage.getItem(cb.dataset.k)==='1';
    cb.onchange=()=>localStorage.setItem(cb.dataset.k, cb.checked?'1':'0'); });

  go(0);
</script>
</body>
</html>
```

- [ ] **Step 2: Insert the untimed cards (dry-run checklist + fallback) where the comment marker is**

Replace the line `  <!-- CARDS GET INSERTED HERE IN STEPS 2–4 -->` with these two always-visible cards followed by the step cards from Step 3 and Step 4. Insert this block first:

```html
  <div class="card checklist">
    <h2 style="margin-top:0">Dry-run for yourself first ✅</h2>
    <p style="color:#666">Tick each as you confirm it in your own GitHub repo. State is saved in this browser.</p>
    <ul style="list-style:none;padding-left:0">
      <li><label><input type="checkbox" data-k="dr1"> Pushed this repo to my GitHub account</label></li>
      <li><label><input type="checkbox" data-k="dr2"> Built tests.yml live from blank → first green run</label></li>
      <li><label><input type="checkbox" data-k="dr3"> Opened .github/workflows/tests.yml on GitHub and pointed at it</label></li>
      <li><label><input type="checkbox" data-k="dr4"> Added pull_request + workflow_dispatch; clicked Run workflow</label></li>
      <li><label><input type="checkbox" data-k="dr5"> Broke apply_discount → saw red ✗ on a PR → reverted → green ✓</label></li>
      <li><label><input type="checkbox" data-k="dr6"> Added the matrix; saw 3 jobs run</label></li>
      <li><label><input type="checkbox" data-k="dr7"> Added badge + artifact; downloaded the report</label></li>
      <li><label><input type="checkbox" data-k="dr8"> Timed myself — finished within 60 minutes</label></li>
    </ul>
  </div>

  <div class="card fallback">
    <h2 style="margin-top:0">If wifi / Actions is slow ⚠️</h2>
    <div class="zone say"><div class="label">Say this</div><p>"While that runs, here's exactly what you'll see." </p></div>
    <p>Point at these mock run rows and keep talking; the real run will catch up.</p>
    <div class="runrow"><span class="dot green"></span> Tests · main · passed in 14s</div>
    <div class="runrow"><span class="dot red"></span> Tests · fix-discount · failed in 12s — 1 test failed</div>
    <p style="color:#666">Backup copies of every stage are in <code>.github/workflows/stages/</code> (v1–v4) if you need to paste a known-good file.</p>
  </div>
```

- [ ] **Step 3: Insert step cards 1–4 (intro → Stage 1 → show folder → first green run)**

Immediately after the fallback card, insert:

```html
  <div class="card step" data-short="What is CI">
    <div class="head"><span class="stage">Intro · 1 of 8</span><span class="clock">aim: 0:00–0:08</span></div>
    <div class="zone say"><div class="label">Say this</div><p>"Everyone here runs tests by hand. Today we hand that job to a robot that runs them for us — every time the code changes. That robot is GitHub Actions. It lives inside your repo, as one text file."</p></div>
    <div class="zone show"><div class="label">Show them — where it lives</div>
      <div class="tree">
        <div>📁 gha-for-testers</div>
        <div>&nbsp;&nbsp;📁 src</div>
        <div>&nbsp;&nbsp;📁 tests</div>
        <div>&nbsp;&nbsp;📁 .github</div>
        <div>&nbsp;&nbsp;&nbsp;&nbsp;📁 workflows</div>
        <div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="hi">📄 tests.yml</span> ← the whole configuration</div>
      </div>
      <p>"GitHub looks in exactly one place — <code>.github/workflows</code>. Any <code>.yml</code> file here becomes a workflow."</p>
      <span class="aha">Aha: "It's not scary infrastructure — it's one file in one folder."</span>
    </div>
  </div>

  <div class="card step" data-short="Stage 1 build">
    <div class="head"><span class="stage">Stage 1 · 2 of 8</span><span class="clock">aim: 0:08–0:25</span></div>
    <div class="zone say"><div class="label">Say this</div><p>"Watch me build it from nothing. I'll type each line and tell you what it means. You do NOT make the folder — GitHub creates it for you the moment you commit."</p></div>
    <div class="zone do"><div class="label">Do this</div>
      <p>Click the <b>Actions</b> tab → <b>set up a workflow yourself</b>. Delete the sample. Rename the file to <b>tests.yml</b>. Type:</p>
      <pre>name: Tests
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
      - run: pytest</pre>
      <p>Then click the green <b>Commit changes…</b> button → <b>Commit changes</b>.</p>
    </div>
    <div class="zone show"><div class="label">Show them</div>
      <p>Narrate as you type: "<b>name</b> is just a label. <b>on: push</b> is WHEN — every push. <b>jobs</b> → one job called test. <b>runs-on</b> is WHICH machine. <b>steps</b> are WHAT, in order: get the code, install Python, install pytest, run pytest."</p>
      <span class="aha">Aha: "That's the whole file. Five ideas: name, on, jobs, runs-on, steps."</span>
    </div>
  </div>

  <div class="card step" data-short="Show the folder">
    <div class="head"><span class="stage">Stage 1 · 3 of 8</span><span class="clock">aim: ~0:20</span></div>
    <div class="zone say"><div class="label">Say this</div><p>"Remember I said GitHub makes the folder? Let's go look — it's really there now."</p></div>
    <div class="zone do"><div class="label">Do this</div><p>Click the <b>Code</b> tab. Click the <b>.github</b> folder → <b>workflows</b> folder → <b>tests.yml</b>.</p></div>
    <div class="zone show"><div class="label">Show them</div>
      <p>Point at the path breadcrumb <code>.github / workflows / tests.yml</code>: "This is the entire configuration. One file, one folder — and I never created the folder myself."</p>
      <span class="aha">Aha: "Committing the file created the folder. That's all the setup there is."</span>
    </div>
  </div>

  <div class="card step" data-short="First green run">
    <div class="head"><span class="stage">Stage 1 · 4 of 8</span><span class="clock">aim: ~0:23</span></div>
    <div class="zone say"><div class="label">Say this</div><p>"The moment I committed, the robot started. Let's watch it."</p></div>
    <div class="zone do"><div class="label">Do this</div><p>Click the <b>Actions</b> tab. Click the newest run at the top. Click the <b>test</b> job to expand the steps.</p></div>
    <div class="zone show"><div class="label">Show them</div>
      <p>Point at the status: "A yellow dot means it's running… now a <b>green tick</b> — every test passed, and nobody touched a keyboard. Click a step to see the actual pytest output."</p>
      <span class="aha">Aha: "That's continuous integration. That's the whole idea."</span>
    </div>
  </div>
```

- [ ] **Step 4: Insert step cards 5–8 (Stage 2 red→green → matrix → badge/artifact → recap)**

Immediately after card 4, insert:

```html
  <div class="card step" data-short="Stage 2 PR gate">
    <div class="head"><span class="stage">Stage 2 · 5 of 8</span><span class="clock">aim: 0:25–0:38</span></div>
    <div class="zone say"><div class="label">Say this</div><p>"Right now it runs on a push. But the real power is stopping a broken change BEFORE it merges. Let's make it run on pull requests too — and give ourselves a manual button."</p></div>
    <div class="zone do"><div class="label">Do this — edit the triggers</div>
      <p><b>Actions</b> is done; go to <b>Code</b> → open <code>.github/workflows/tests.yml</code> → click the pencil ✏️. Replace the <code>on: push</code> line with:</p>
      <pre>on:
  push:
  pull_request:
  workflow_dispatch:</pre>
      <p>Commit. Now click <b>Actions</b> → <b>Tests</b> → the <b>Run workflow</b> button appeared — that's <code>workflow_dispatch</code>. Click it to run on demand.</p>
    </div>
    <div class="zone do"><div class="label">Do this — break it on a branch</div>
      <p>Go to <b>Code</b> → open <code>src/cart.py</code> → pencil ✏️. Change this one line:</p>
      <pre>return round(amount * (1 - percent / 100), 2)</pre>
      <p>to (a real bug — it forgets the discount):</p>
      <pre>return round(amount, 2)</pre>
      <p>Under "Commit changes", choose <b>Create a new branch</b> (e.g. <code>fix-discount</code>) → <b>Propose changes</b> → <b>Create pull request</b>.</p>
    </div>
    <div class="zone show"><div class="label">Show them</div>
      <p>On the PR, point at the checks box: "Yellow… now a <b>red ✗</b>. The robot ran our tests on my change and one failed — <code>test_apply_discount</code>. GitHub is telling us: don't merge this."</p>
      <p>Then fix it: edit the branch's <code>cart.py</code> back to the correct line, commit. Watch the check go <b>green ✓</b>. Merge.</p>
      <span class="aha">Aha: "The test caught my bug automatically — that's the safety net."</span>
    </div>
  </div>

  <div class="card step" data-short="Stage 3 matrix">
    <div class="head"><span class="stage">Stage 3 · 6 of 8</span><span class="clock">aim: 0:38–0:48</span></div>
    <div class="zone say"><div class="label">Say this</div><p>"Our users aren't all on one Python version. Watch us test three at once — from one push."</p></div>
    <div class="zone do"><div class="label">Do this</div>
      <p>Edit <code>tests.yml</code>. Under <code>test:</code>, add a <code>strategy</code> block and swap the fixed version for the matrix value:</p>
      <pre>    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]</pre>
      <p>Change the setup-python <code>python-version:</code> line to:</p>
      <pre>          python-version: ${{ matrix.python-version }}</pre>
      <p>Commit. (Full file is <code>stages/v3-matrix.yml</code> if you need it.)</p>
    </div>
    <div class="zone show"><div class="label">Show them</div>
      <p>In <b>Actions</b>, point at the run: "One push — but three jobs, one per version, running in parallel. Each gets its own green tick."</p>
      <span class="aha">Aha: "Coverage across versions for free — you just listed them."</span>
    </div>
  </div>

  <div class="card step" data-short="Stage 4 badge">
    <div class="head"><span class="stage">Stage 4 · 7 of 8</span><span class="clock">aim: 0:48–0:54</span></div>
    <div class="zone say"><div class="label">Say this</div><p>"Two finishing touches testers love: a live badge that proves we're green, and a saved test report you can download."</p></div>
    <div class="zone do"><div class="label">Do this</div>
      <p>Edit <code>tests.yml</code>: change <code>- run: pytest</code> to produce a report and add an upload step:</p>
      <pre>      - run: pytest --junitxml=report.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-report-${{ matrix.python-version }}
          path: report.xml</pre>
      <p>Commit. Then edit <code>README.md</code> and replace <code>OWNER/REPO</code> in the badge line with your username and repo. Commit.</p>
    </div>
    <div class="zone show"><div class="label">Show them</div>
      <p>Show the README badge going green. In the latest <b>Actions</b> run, scroll to <b>Artifacts</b> and download <code>test-report-3.12</code>. Mention: "You can also run this on a timer with <code>schedule:</code> — e.g. every night."</p>
      <span class="aha">Aha: "Now anyone can see we're green, and every run keeps its receipts."</span>
    </div>
  </div>

  <div class="card step" data-short="Recap">
    <div class="head"><span class="stage">Recap · 8 of 8</span><span class="clock">aim: 0:54–1:00</span></div>
    <div class="zone say"><div class="label">Say this</div><p>"In one hour we answered four questions. What is it? A robot that runs your tests. Where does it live? One .yml file in .github/workflows. How is it triggered? push, pull_request, the manual button, and schedule. How do you write it? name, on, jobs, runs-on, steps — mind the indentation."</p></div>
    <div class="zone do"><div class="label">Do this</div><p>Share the repo link and hand out <code>CHEATSHEET.md</code>. Open the floor for questions.</p></div>
    <div class="zone show"><div class="label">Show them</div><p>Flip back to the green matrix run and the badge as the closing image.</p><span class="aha">Aha: "You could set this up on your own project this afternoon."</span></div>
  </div>
```

- [ ] **Step 5: Verify the presenter is complete and self-contained**

Run:
```bash
grep -c 'class="card step"' facilitator.html   # expect 8
grep -q "you do NOT make the folder" facilitator.html && echo "spoon-fed folder note present (any case)" || grep -qi "do NOT make the folder" facilitator.html && echo "folder note OK"
grep -qi "return round(amount, 2)" facilitator.html && echo "break edit present OK"
grep -qi "workflow_dispatch" facilitator.html && echo "manual trigger taught OK"
grep -qi "http" facilitator.html && echo "WARNING: external URL found — must be self-contained" || echo "no external URLs OK"
```
Expected: `8`; the folder-note line; break-edit OK; manual-trigger OK; and "no external URLs OK".

- [ ] **Step 6: Open it and click through all 8 cards to confirm nav + copy buttons work**

Open `facilitator.html` in a browser (double-click, or `open facilitator.html` on macOS). Confirm: the glossary strip is pinned at top; Prev/Next and arrow keys move through 8 step cards; the rail highlights the current card; a Copy button copies a YAML block; the checklist ticks persist after reload.

- [ ] **Step 7: Commit**

```bash
git add facilitator.html
git commit -m "Add scripted spoon-fed facilitator presenter"
```

---

## Self-Review

**Spec coverage:**
- §1 four objectives → Recap card + Cards 1/2/3/5 (what, where, triggers, YAML). ✓
- §3 sample repo (src/cart.py, tests, requirements, README, facilitator, cheatsheet, stages) → Tasks 1, 2, 3, 4. ✓
- §3 stages inert in subfolder → Task 2 Step 5 asserts no top-level workflow. ✓
- §4 four stages (push / triggers+PR gate / matrix / badge+artifact) → Task 2 files + Task 4 cards 2,5,6,7. ✓
- §5 timing → clock labels on every step card. ✓
- §6 facilitator.html (TALK/DO/SHOW, pace clock, teleprompter nav, file-tree, dry-run checklist, glossary, fallback, print CSS) → Task 4. ✓ (Fallback uses CSS-drawn run rows instead of pre-captured screenshots, since real screenshots require a live run the facilitator does on their dry-run; the `stages/` files are the paste-in safety net. This is the one deliberate realisation choice vs. the spec's "embedded screenshots".)
- §6 spoon-fed / folder auto-created note → Card 2 + Card 3. ✓
- §6 CHEATSHEET → Task 3. ✓
- §7 solo dry-run → checklist card. ✓
- §8 prerequisites → README run instructions + badge placeholder. ✓

**Placeholder scan:** No TBD/TODO. `OWNER/REPO` in README is an intentional, documented placeholder the facilitator fills with their own repo — not a plan gap.

**Type consistency:** `add_item / total / apply_discount` used identically in Task 1 tests, implementation, and the Card 5 break edit. The break edit line matches `src/cart.py` verbatim. Workflow field names (`runs-on`, `matrix.python-version`, `upload-artifact@v4` unique name) are consistent between Task 2 files and Task 4 cards.
