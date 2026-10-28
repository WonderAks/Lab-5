# Lab 5 — Reflection

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the mechanical Pylint/Flake8 items — removing the unused `sys` import,
renaming `createAccount` to `create_account`, `== None` → `is None`, adding docstrings
and the final newline, and wrapping the long line. Each had a single obvious fix that
the tool's message practically spelled out, and none could change behaviour.

**Hardest:** the ones where the tool pointed at a symptom but the fix needed a design
decision:

- **`eval()` in `compute_bonus` (B307).** Bandit suggests `ast.literal_eval`, but that
  cannot evaluate `bal * 0.05`. The real fix was changing the function's contract to
  take a `rate`, which also removed the "unused variable `bal`" warning that was only a
  side effect of `eval`.
- **MD5 PIN hashing (B324).** Silencing the warning with `usedforsecurity=False` would
  have been wrong. The correct fix needed a salted, slow hash (PBKDF2) and a matching
  `verify_pin()` using a constant-time comparison.
- **The unused `service_fee`.** Pylint and Flake8 only say "unused variable". Deleting it
  would have made the warning vanish but kept a business bug (withdrawals were free).
  Someone had to decide that the fee was *meant* to be charged and change `withdraw()`
  so it checks and deducts `amount + fee`.

## 2. Did the tools report any false positives?

In this file almost every finding was a real problem, but a few are **context-dependent**:

- **B324 (MD5)** and **B311 (`random`)** would be false positives if the value were not
  security-related (e.g. MD5 as a cache key, `random` for a shuffled demo list). Here a
  PIN hash and a temporary PIN *are* security values, so they were true positives.
- **B105 (hardcoded password)** is a name-based heuristic (the variable is called
  `admin_token`). Bandit rated it only Low/Medium confidence, yet in this program the
  string really was a secret, so it was correct — but the same check fires on harmless
  constants like `PASSWORD_FIELD = "password"`.
- **Pylint C0116 (missing docstring)** on one-line helpers and **R1705 (no-else-return)**
  are style opinions rather than defects; I fixed them, but a team could reasonably
  disable them.
- Severity labels can also mislead in the other direction: Bandit rates `eval` Medium and
  the hardcoded secret Low, although both are serious in a banking context.

The more important observation is the **false negatives**: none of the tools flagged that
the admin token is printed to the console, that the service fee is never charged, or that
the demo runs on import. I found those by running the program and reading the output.

## 3. How would you integrate static analysis into a real development workflow?

- **Locally:** editor integration (Pylint/Flake8 in VS Code) so issues show up while
  typing, plus a **pre-commit** hook running Flake8 and Bandit so bad code never enters
  a commit.
- **In CI:** a GitHub Actions job on every pull request that runs all three tools and
  fails the build on any Bandit High/Medium finding, any Flake8 error, or a Pylint
  score below an agreed threshold (e.g. 9.5). The reports are uploaded as artifacts.
- **Configuration in the repo** (`pyproject.toml` / `.flake8` / `.bandit`) so everyone
  shares the same rules. Disabling a rule is allowed only with a targeted
  `# nosec` / `# noqa` and a written justification, never blanket ignores.
- **Complement, not replace:** keep unit tests and code review, because the tools missed
  the logic bugs described above. For an existing legacy codebase, start by failing only
  on new issues and burn down the backlog gradually so developers do not learn to ignore
  the tool.

## 4. What tangible improvements did you see in code quality, readability, and robustness?

- **Measurable:** Pylint 5.62 → 10.00, Bandit 6 findings (2 High) → 0, Flake8 7 → 0.
- **Security:** no shell execution, no `eval`, salted PBKDF2 instead of MD5, secure
  random PINs, and no secret in the source or in the output.
- **Robustness:** `deposit()` and `withdraw()` now return clear `True`/`False` results
  and reject unknown accounts and non-positive amounts instead of silently swallowing
  errors; the shared mutable ledger bug is gone; the backup file is always closed.
- **Readability and testability:** PEP 8 names, docstrings, f-strings, flatter control
  flow, and a `__main__` guard so the module can be imported and unit-tested without
  side effects. I verified the behaviour with a quick script (create, duplicate id,
  deposit, withdraw with fee, insufficient funds, bonus, PIN hash/verify).
- **Caveat:** a clean report does not prove the program is correct. The service-fee and
  token-printing problems survived every tool and needed manual review, so static
  analysis is a strong first filter, not a substitute for testing.
