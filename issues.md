# Lab 5 — Issue Documentation Table

**File analysed:** `bank_account_system.py` (line numbers refer to the **original** file)
**Tools:** Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1

Issues are ordered by severity (High → Medium → Low). "Tool" lists every tool that
reported the issue; "none" means I found it by running and reading the program
rather than from a tool report.

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 1 | Shell command built from a string (`os.system`) | Security — **High** (Bandit B605) | 55 | `os.system("echo Backup complete: " + filename)` starts a shell and concatenates the filename into the command. A filename such as `x; rm -rf ~` would be executed (command injection). It is also pointless: `print` does the same job. | Removed `os.system` and the `os` import use for it; replaced with `print(f"Backup complete: {filename}")`. *(Bandit commit)* |
| 2 | Weak hash (MD5) for PINs | Security — **High** (Bandit B324) | 43–44 | MD5 is fast and broken; unsalted, so identical PINs give identical hashes and a 4-digit PIN can be reversed instantly with a lookup table. | Replaced with salted PBKDF2-HMAC-SHA256 (200,000 rounds, random 16-byte salt) from the standard library; added `verify_pin()` using constant-time `hmac.compare_digest`. *(Bandit commit)* |
| 3 | Secret token printed to the console | Security / Logic — **High** (none — found by running the program) | 67 | `print("Token initialized:", admin_token)` writes the admin secret to stdout, where it ends up in terminal history and logs. No tool flags this. | Token is no longer printed. The program now only reports whether it is configured (`Admin token configured: True/False`). *(Bandit commit)* |
| 4 | `eval()` on a caller-supplied string | Security — **Medium** (Bandit B307, Pylint W0123) | 37–40 | `compute_bonus(acc_id, expr)` runs arbitrary Python from `expr`; anyone who controls it controls the program. | Redesigned the API: `compute_bonus(acc_id, rate)` returns `balance * rate`. No code evaluation at all. *(Bandit commit)* |
| 5 | Service fee never charged | Logic bug — **Medium** (Pylint W0612, Flake8 F841 only flag it as "unused") | 27, 33 | `service_fee = 2.50` is defined but never applied, so withdrawals are silently free; the tools only see an unused variable, not the missing business rule. | Promoted to a module constant `SERVICE_FEE`; `withdraw()` now requires `balance >= amount + fee` and deducts both. *(Pylint commit)* |
| 6 | Mutable default argument | Bug — **Medium** (Pylint W0102) | 11 | `transactions=[]` is created once and shared by every call, so unrelated callers corrupt each other's ledger. | Default changed to `None`; falls back to a module-level `ledger` list. *(Pylint commit)* |
| 7 | Bare `except` that swallows every error | Reliability — **Medium** (Pylint W0702, Flake8 E722, Bandit B110) | 20–23 | `deposit()` ignores *all* failures (unknown account, wrong type, even Ctrl-C), so the caller cannot tell whether the money arrived. | Removed try/except; explicit checks (account exists, amount > 0), returns `True`/`False` like `withdraw()`. *(Pylint commit)* |
| 8 | Hardcoded secret in source | Security — Low by Bandit, serious in practice (Bandit B105) | 59 | `admin_token = "SUPER_SECRET_BANK_TOKEN_2026"` is committed to version control for anyone to read. | Read from the `BANK_ADMIN_TOKEN` environment variable via `os.environ.get`. *(Bandit commit)* |
| 9 | Predictable random number generator for PINs | Security — Low (Bandit B311) | 47–48 | `random` (Mersenne Twister) is predictable and not meant for security values. | Replaced with `secrets.randbelow(9000) + 1000` (same 1000–9999 range). *(Bandit commit)* |
| 10 | File not closed safely / no encoding | Reliability — Low (Pylint R1732, W1514) | 52–54 | `open()` + manual `close()` leaks the handle if `write` raises; encoding depends on the OS locale. | `with open(filename, "w", encoding="utf-8") as backup_file:`. *(Pylint commit)* |
| 11 | Unused local variable `bal` | Maintainability — Low (Pylint W0612, Flake8 F841) | 38 | `bal` looks unused to the tools because it is only consumed implicitly by `eval(expr)`. A symptom of issue 4. | Disappeared with the `eval` removal (issue 4). *(Bandit commit)* |
| 12 | Function name not snake_case | Convention — Low (Pylint C0103) | 11 | `createAccount` violates PEP 8 naming. | Renamed to `create_account` and updated the caller. *(Pylint commit)* |
| 13 | Missing docstrings | Convention — Low (Pylint C0116 ×8) | 11, 19, 26, 37, 43, 47, 51, 58 | No function says what it does, returns, or when it fails. | Added a one-line docstring to every function. *(Pylint commit)* |
| 14 | Comparison to `None` with `==` | Convention — Low (Pylint C0121, Flake8 E711) | 28 | `== None` can be fooled by custom `__eq__`; PEP 8 says use `is`. | Rewritten as `account is None`. *(Pylint commit)* |
| 15 | Unnecessary `else` after `return` | Refactor — Low (Pylint R1705) | 30–34 | Extra nesting adds no value. | Flattened the control flow in `withdraw()`. *(Pylint commit)* |
| 16 | `%`-formatting | Convention — Low (Pylint C0209) | 15 | Old-style format; `%d` also silently truncates float balances (e.g. 1000.75 → 1000) in the ledger text. | Converted to an f-string, which prints the true amount. *(Pylint commit)* |
| 17 | Unused import `sys` | Maintainability — Low (Pylint W0611, Flake8 F401) | 6 | Dead import. | Deleted. *(Pylint commit)* |
| 18 | Line too long (89 > 79) | Style — Low (Flake8 E501) | 15 | Hard to read in side-by-side diffs. | Wrapped across three lines (after the f-string change it was still 83 chars). *(Flake8 commit)* |
| 19 | Missing newline at end of file | Style — Low (Pylint C0304, Flake8 W292) | 70 | POSIX/PEP 8 convention; avoids noisy diffs. | Added trailing newline. *(Pylint commit)* |
| 20 | `main()` runs on import | Design — Low (none) | 70 | A bare `main()` call executes the whole demo (and writes `backup.txt`) whenever the module is imported, making it untestable. | Wrapped in `if __name__ == "__main__":`. *(Pylint commit)* |

## Results: before vs after

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.62 / 10 (21 messages) | **10.00 / 10** (0 messages) |
| Bandit | 6 issues (2 High, 1 Medium, 3 Low) | **0 issues** |
| Flake8 | 7 issues | **0 issues** (empty report) |

All 20 documented issues are fixed (the lab requires at least 4). Reports are in `reports/`.
Output of the program changed in two intentional ways: the bonus is now `64.875`
instead of `65.0` because withdrawals now cost the 2.50 service fee (issue 5), and the
secret token is no longer printed (issue 3).
