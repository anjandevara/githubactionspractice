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
