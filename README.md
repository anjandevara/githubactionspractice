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

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pytest

## Where the automation lives

    .github/
      workflows/
        tests.yml   ← the whole configuration is this one file

`.github/workflows/stages/` holds reference copies of each stage (v1–v4). They sit
in a subfolder on purpose: GitHub only runs `.yml` files at the top level of
`.github/workflows/`, so these copies never run — they are just safety-net examples.

## The four triggers

The `on:` block decides *when* a workflow runs:

- **push** — every time you push commits.
- **pull_request** — when a PR opens or updates (this is what blocks a broken merge).
- **workflow_dispatch** — adds a manual **Run workflow** button in the Actions tab.
- **schedule** — on a timer, e.g. nightly.

For more than one trigger, `on:` must be a *block* with each trigger indented under it:

    on:
      push:
      pull_request:
      workflow_dispatch:

## Common YAML gotchas

Indentation is structure, not decoration — these are the mistakes that bite most:

1. **Triggers collapse.** `on: pull_request` (value on the same line) only sets one
   trigger. Listing several requires the block form above, each trigger indented under `on:`.
2. **`jobs:` must stay at the top level.** A workflow has exactly three keys at the far
   left (column 0): `name`, `on`, `jobs`. If `jobs:` drifts right, it becomes a child of
   whatever is above it and GitHub reports "workflow must contain jobs".
3. **Matrix = define once, use once.** Put the *list* of versions under
   `strategy.matrix`, and pull one value out in the step with an expression:

        strategy:
          matrix:
            python-version: ["3.10", "3.11", "3.12"]   # define the list here
        ...
              python-version: ${{ matrix.python-version }}   # use one value here

   The two lines are deliberately different. `${{ ... }}` only ever *reads* a value —
   it can never be the place you define it.
4. **Spaces, never tabs.** Line things up in 2-space steps.

When in doubt, diff your file against the matching `.github/workflows/stages/v*.yml`.
