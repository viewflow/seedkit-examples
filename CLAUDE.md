# seedkit-examples

Generated Django projects plus the harness that produces them. The skill under test lives in the
sibling [seedkit](https://github.com/viewflow/seedkit) repo — `$SEEDKIT`, default `../seedkit` — which
owns `skills/`, `testcases/`, and the CHANGELOG. Nothing in this repo ships with the plugin.

Layout:
- `NN-*/` — one generated project per testcase, committed. `baselines/<model>/NN-*/` — the control arm.
- `train/` — the harness: `run-tests.sh` pipes each testcase through an agent CLI and writes per-run
  logs; `run-baseline.sh` generates the no-skill control arm; `run-reproduce.sh` re-boots committed
  projects; `review-logs.sh` auto-patches the skill from those logs; `agents.sh` is the shared
  multi-CLI (claude/codex/agy) dispatch the four scripts source.
- `logs/` — per-run logs, gitignored.
- `results-<cli>.tsv` — one row per (case, arm, model).

Three path variables, resolved in every script's prologue: `WORKSPACE` (this repo, where projects
land), `SEEDKIT` (the skill repo, read-only except from `review-logs.sh`), and `TESTCASES`
(`$SEEDKIT/testcases`). Both are overridable by env var.

## train/run-tests.sh contract

Each case runs in its own session (portable `setsid_exec` Python shim, `train/agents.sh`) so the
post-case sweep `kill -- -$pgid` reaches every descendant — orphaned celery workers, gunicorn,
`runserver` autoreloader. A watchdog terminates the group if a phase overruns — `TIMEOUT_PER_PHASE` in
`run-tests.sh`, `TIMEOUT_PER_CASE` in `run-baseline.sh`, both 7200. Cleanup is harness-side; the skill
and testcase prompts must not invoke `pkill -f` (it matches the parent agent-CLI process).

`cli_dispatch` appends the agent CLI's stderr to the case log — session/usage limits, auth failures,
and network errors are reported there, and the stdout `jq | tee` pipeline never sees them. After the
generation phase both scripts call `assert_agent_ran()`: zero `[tool:…]` markers means the CLI never
got a turn, so the harness writes no result row and aborts the sweep with exit 3. A generation phase
that reaches a project always calls tools, and whatever stopped one case stops every later one within
seconds — recording those would fill the table with infrastructure failures dressed as failed builds.

`assert_phase_ok()` catches the other half of that class: an agent that worked for 200 tool calls and
then lost its connection. `claude -p` exits 0 whenever the agent completes its turn, whatever it
concluded about the project — a project that won't boot still exits 0, and shows up in the score
instead. So a non-zero exit from any phase is the CLI failing, never a build result, and it aborts the
sweep the same way. That is also why the TSV carries no exit column: with the guard in place a written
row could only ever hold `0`. Nothing in the harness measures boot success directly.

Only one harness script may hold a workspace at a time — `acquire_workspace_lock()` takes
`$WORKSPACE/.harness-lock` (a `mkdir`, since macOS ships no `flock`) and every script calls it.
`run-tests.sh` identifies each case's output by mtime, so a second script writing the same tree makes a
sibling look like this case's project, and review, scorecard, and the README prepend all follow the
wrong path.

Generated projects land here, at the repo root. Per-run logs land in `logs/` (gitignored). The harness
prepends each testcase's `## Prompt` block to the generated project's `README.md` and rewrites the
top-level `README.md` index after every run — edit that text in `run-tests.sh`, not in `README.md`,
and keep `train` in the index's skip list.

## Baseline contract

`run-baseline.sh` is the control arm: same `## Prompt`, same `## Boot check`, same auto-fix
instruction, no skill. The two arms must differ in one variable only, so anything given to one is given
to both.

- Output goes to `baselines/<model>/<case>/` — `model_slug()` in `agents.sh` turns `claude-sonnet-5-5`
  into `sonnet` — so the control arm publishes with the skill arm and each model's control sits beside
  the others instead of overwriting them. That sits under the `.claude/skills/django-seedkit` symlink
  `run-tests.sh` creates, so `unlink_skill()` removes the project-scoped symlinks before the run and
  `assert_skill_unreachable()` walks up from the baseline root and refuses to start if anything is
  still reachable (a hand-placed real directory, or a global install under `~/.claude/skills/` or
  `~/.gemini/config/plugins/`). `run-tests.sh` recreates the symlink at the top of its next run, so the
  removal costs nothing. The two scripts can't run concurrently anyway — they share one workspace lock.
- Baseline logs go to `logs/baselines/`: inside the wholesale-gitignored `logs/`, and outside
  `review-logs.sh`'s non-recursive `logs/*.log` glob. `review-logs.sh` also rejects any `baseline-*.log`
  by name and any log with no `BUILD` phase, so an explicit argument can't get one through either.
- Both arms are graded on `train/scorecard.md` — eight arm-neutral static checks emitting `SCORE n/8`.
  The testcase's `## Review` section is skill-arm-only; it asserts structure the control was never
  asked for.
- Both arms write to one `results-<cli>.tsv` (`case / arm / cli / model / score / build_s /
  tool_calls / fixes / rewrites / run_at`); the `arm` column separates them, so comparing is
  `column -t < results-claude.tsv`. Split per CLI because comparing a claude skill run against a codex
  baseline measures the CLI, not the skill.
- Every claude invocation carries `--settings '{"advisorModel":""}'` (`CLAUDE_HARNESS_SETTINGS` in
  `agents.sh`), for the same reason as `CLAUDE_CODE_DISABLE_AUTO_MEMORY`: operator config must not
  shape a harness run. `advisorModel` is a user setting, so on a machine that sets it the build agent
  can consult a stronger model on demand — making the `model` column a lie for both arms, and in the
  control arm supplying exactly the scaffolding guidance the skill does. `--disallowedTools advisor`
  does not work; the advisor is not a permission-system tool.
- Generation phases (build and baseline) pass `CASE_DENY='Bash(git:*)'` (`GENERATION_DENY` in
  `agents.sh`). The build agent works in this repo, a git repo holding every earlier generated project,
  so `git log` / `git show` hand it prior outputs to copy from. Deny rules win over
  `--dangerously-skip-permissions`. It is opt-in per caller because `review-logs.sh` commits and pushes
  through the same dispatcher and must keep git. Both generation prompts also forbid reading sibling
  directories — denying git closes one route to earlier outputs, the prompt closes the rest.
- `build_s`, `tool_calls`, `fixes`, and `rewrites` are **build-phase only**, captured before review and
  scorecard run. Only the skill arm has a `## Review` phase, so a wall-clock total would charge it for
  verification the control never performs and make the skill read as slower. `tool_calls` counts
  `[tool:…]` markers in the log — reaching a working project in fewer loops is an outcome the skill
  gets credit for, not just reaching it. Any metric added later goes in the same place, for the same
  reason.
- `fixes` is the metric to watch when iterating on the skill; `score` is not. The scorecard is a floor
  test the skill passes by construction — it reads 8/8 in every scored case and has never once failed a
  check against skill output, so it separates the arms and then stops moving. A fix, by contrast, is a
  reference file that was wrong: the agent had to repair its own output. `fix_report_block()` in
  `agents.sh` supplies the `FIXES n` tail both generation prompts end with — shared rather than
  duplicated, because the arms must differ in one variable only. `rewrites` is its witness: `fixes` is
  self-reported by the agent under test and undercounts (agents file routine repairs under "Notes" and
  report zero), while `rewrites` counts writes to a path already written this run, from `[file:…]`
  markers `cli_dispatch` emits. Read them together — one number the agent chose, one it didn't.
- `upsert_result()` (`agents.sh`) **replaces** the row for a `(case, arm, model)` triple. Re-running a
  case after a skill fix updates its row in place — appending would leave the stale result beside the
  new one and every comparison would read both. Model is part of the key because baselines are
  per-model: without it an opus control run silently overwrites the sonnet one it exists to be compared
  against. The file stays sorted on the same three fields so the committed diff is legible.

## review-logs.sh and the skill repo

`review-logs.sh` is the only script that writes to `$SEEDKIT`. It refuses to start when that checkout
has uncommitted changes, then per log asks an agent to patch `SKILL.md`, a reference, or a testcase,
bump the version in `plugin.json` + `SKILL.md` frontmatter, extend today's CHANGELOG section, and
commit + push — all inside `$SEEDKIT`, one commit per iteration. That is why `testcases/` stays in the
skill repo: a testcase edit has to land in the same commit as the reference fix that motivated it.

## Committing

Refresh the examples after a clean run:

```sh
git add -A && git commit -m "refresh: $(date -u +%Y-%m-%d) run" && git push
```

This repo and `seedkit/` are sibling submodules of `RobustaRush/Robusta`, neither nested in the other.
Commit here and stop — the parent pointer bump is the user's.
