"""Bank account management module."""
#NAME:Aks Raj Singh
#SRN: PES2UG24CS044
import hashlib
import hmac
import os
import secrets

account_data = {}
ledger = []
SERVICE_FEE = 2.50
PBKDF2_ROUNDS = 200_000


def create_account(acc_id, name, initial_deposit=0, transactions=None):
    """Create an account and log it; return False if the id already exists."""
    if acc_id in account_data:
        return False
    if transactions is None:
        transactions = ledger
    account_data[acc_id] = {"name": name, "balance": initial_deposit}
    transactions.append(
        f"Created {acc_id} with initial balance {initial_deposit}"
    )
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


def compute_bonus(acc_id, rate):
    """Return the promotional bonus: the account balance times a rate."""
    return account_data[acc_id]["balance"] * rate


def get_hash(pin, salt=None):
    """Return 'salt$hash' for a PIN using salted PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, PBKDF2_ROUNDS)
    return f"{salt.hex()}${digest.hex()}"


def verify_pin(pin, stored_hash):
    """Check a PIN against a value produced by get_hash."""
    salt_hex, _ = stored_hash.split("$")
    candidate = get_hash(pin, bytes.fromhex(salt_hex))
    return hmac.compare_digest(candidate, stored_hash)


def generate_temp_pin():
    """Return a cryptographically secure four-digit temporary PIN."""
    return secrets.randbelow(9000) + 1000


def backup_data(filename="backup.txt"):
    """Write all account data to a file and announce completion."""
    with open(filename, "w", encoding="utf-8") as backup_file:
        backup_file.write(str(account_data))
    print(f"Backup complete: {filename}")


def main():
    """Run a small demonstration of the banking functions."""
    admin_token = os.environ.get("BANK_ADMIN_TOKEN")
    create_account("A01", "Alice", 1000)
    deposit("A01", 500)
    withdraw("A01", 200)
    print("Bonus:", compute_bonus("A01", 0.05))
    print("PIN Hash:", get_hash("1234"))
    print("Temp PIN:", generate_temp_pin())
    backup_data()
    print("Admin token configured:", admin_token is not None)


if __name__ == "__main__":
    main()
