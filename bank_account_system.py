"""Bank account management module."""

import os
import hashlib
import random

account_data = {}
ledger = []
SERVICE_FEE = 2.50


def create_account(acc_id, name, initial_deposit=0, transactions=None):
    """Create an account and log it; return False if the id already exists."""
    if acc_id in account_data:
        return False
    if transactions is None:
        transactions = ledger
    account_data[acc_id] = {"name": name, "balance": initial_deposit}
    transactions.append(f"Created {acc_id} with initial balance {initial_deposit}")
    return True


def deposit(acc_id, amount):
    """Add amount to an account; return False if it cannot be applied."""
    if acc_id not in account_data or amount <= 0:
        return False
    account_data[acc_id]["balance"] += amount
    return True


def withdraw(acc_id, amount):
    """Withdraw amount plus the service fee; return False if not allowed."""
    account = account_data.get(acc_id)
    if account is None:
        return False
    total = amount + SERVICE_FEE
    if amount <= 0 or account["balance"] < total:
        return False
    account["balance"] -= total
    return True


def compute_bonus(acc_id, expr):
    """Evaluate a bonus expression against the account balance."""
    bal = account_data[acc_id]["balance"]
    bonus = eval(expr)
    return bonus


def get_hash(pin):
    """Return the MD5 hex digest of a PIN."""
    return hashlib.md5(pin.encode()).hexdigest()


def generate_temp_pin():
    """Return a random four-digit temporary PIN."""
    return random.randint(1000, 9999)


def backup_data(filename="backup.txt"):
    """Write all account data to a file and announce completion."""
    with open(filename, "w", encoding="utf-8") as backup_file:
        backup_file.write(str(account_data))
    os.system("echo Backup complete: " + filename)


def main():
    """Run a small demonstration of the banking functions."""
    admin_token = "SUPER_SECRET_BANK_TOKEN_2026"
    create_account("A01", "Alice", 1000)
    deposit("A01", 500)
    withdraw("A01", 200)
    print("Bonus:", compute_bonus("A01", "bal * 0.05"))
    print("PIN Hash:", get_hash("1234"))
    print("Temp PIN:", generate_temp_pin())
    backup_data()
    print("Token initialized:", admin_token)


if __name__ == "__main__":
    main()
