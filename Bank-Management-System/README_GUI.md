# Maryam Fahim Bank Management System — Professional GUI

## Run

Open this folder in VS Code and run:

```text
python main.py
```

Windows shortcut:

```text
run_gui.bat
```

No third-party GUI package is required. The interface uses Python Tkinter/ttk and SQLite.

## Demo credentials

### Customer
- Username: `maryam_fahim`
- Password: `Maryam@123`

### Admin
- Username: `maryam_admin`
- Password: `Maryam@Admin123`

## CRUD features

### Admin
- Customers: Create, Read/Search, Update, Block/Unblock, Delete
- Accounts: Create, Read/Search, Update account type, Freeze/Unfreeze, Close, Delete settled accounts
- Transactions: Create Deposit/Withdrawal/Transfer, Read/Search, Update description, safely delete failed records
- CSV reports: Customers, Accounts, Transactions
- Dashboard metrics and recent transactions

### Customer
- View dashboard and balances
- Create/open accounts
- Read account details
- Deposit, withdraw and transfer
- Read transaction history
- Update profile
- Change password

## Banking safety rules

- Account numbers are generated automatically.
- Account opening requires the configured minimum deposit.
- Withdrawals and transfers are balance-checked.
- Closed accounts cannot be reused.
- Completed transaction records are protected from deletion to preserve the audit trail.
- Customer hard-delete removes dependent history only after account settlement/closure.
