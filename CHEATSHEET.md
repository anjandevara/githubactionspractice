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
