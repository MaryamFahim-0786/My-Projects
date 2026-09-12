# 📚 Library Management System

A complete **Command Line Interface (CLI) Library Management System** developed using **Python 3** and **SQLite3**. The system is designed to manage books, members, borrowing, returns, reservations, fines, authentication, and reporting through a structured and user-friendly terminal interface.

---

## ✨ Features

- 📚 **Book Management** — Add, update, delete, search, and manage book records.
- 👥 **Member Management** — Register members, update profiles, manage member status, and handle blocking/unblocking.
- 🔐 **Secure Authentication** — Separate admin and member login with password hashing and login protection.
- 🔄 **Borrow & Return System** — Issue, return, and renew books while automatically updating available quantities.
- 📅 **Due Date Management** — Automatically calculates borrowing and due dates.
- 💰 **Fine Management** — Calculates overdue fines based on the number of overdue days.
- 📌 **Book Reservations** — Members can reserve books and manage reservation status.
- 📊 **Reports & Analytics** — Generate useful reports for books, members, borrowings, fines, and reservations.
- 📄 **CSV Export** — Export system data into CSV files for further use.
- 🗄️ **SQLite Database** — Uses SQLite3 for reliable local data storage.
- 🛡️ **Data Validation** — Validates important user inputs such as email, phone number, ISBN, and other fields.
- 🎨 **User-Friendly CLI** — Organized menus, tables, status indicators, and clear terminal navigation.
- 📝 **Logging** — Maintains system activity and transaction logs.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3** | Main programming language |
| **SQLite3** | Database management |
| **OOP** | Application structure and organization |
| **Hashlib** | Password hashing |
| **Getpass** | Secure password input |
| **CSV** | Report generation and data export |
| **Datetime** | Dates, due dates, and overdue calculations |
| **Decimal** | Accurate fine calculations |
| **Logging** | Application and transaction logging |

The project uses Python's standard library, so no external packages are required.

---

## 📁 Project Structure

```text
Library-Management-System/
│
├── main.py
├── config.py
├── database.py
├── seed_data.py
├── requirements.txt
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── admin.py
│   ├── author.py
│   ├── category.py
│   ├── publisher.py
│   ├── book.py
│   ├── member.py
│   ├── borrowing.py
│   ├── fine.py
│   └── reservation.py
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── book_service.py
│   ├── member_service.py
│   ├── borrowing_service.py
│   ├── fine_service.py
│   └── reservation_service.py
│
├── cli/
│   ├── __init__.py
│   ├── main_menu.py
│   ├── admin_menu.py
│   └── member_menu.py
│
├── reports/
│   ├── __init__.py
│   └── report_generator.py
│
├── data/
│   ├── books_report.csv
│   ├── members_report.csv
│   ├── borrowings_report.csv
│   ├── fines_report.csv
│   └── reservations_report.csv
│
└── tests/
    ├── __init__.py
    └── test_library_system.py
```

---

## 🚀 Installation & Setup

### Requirements

Before running the project, make sure you have:

- Python **3.9 or higher**
- Windows, macOS, or Linux
- No additional Python packages are required

### 1. Clone or Download the Project

Download the project and open the project folder in your terminal or VS Code.

### 2. Open the Project Directory

```bash
cd "Library-Management-System"
```

### 3. Run the Application

```bash
python main.py
```

The SQLite database and initial sample data are created automatically when the application is started.

---

## 🔑 Demo Accounts

### Admin Account

```text
Username: admin
Password: admin123
```

### Member Accounts

| Username | Password | Member |
|---|---|---|
| `alikhan` | `password123` | Ali Khan |
| `sarahahmed` | `password123` | Sarah Ahmed |
| `usman` | `password123` | Muhammad Usman |
| `fatima` | `password123` | Fatima Noor |

New members can also be registered through the application.

---

## 📋 Main System Rules

| Feature | Default Rule |
|---|---|
| Maximum active books per member | 5 |
| Borrowing period | 14 days |
| Maximum renewals | 2 |
| Overdue fine | Rs. 20 per day |
| Duplicate active borrowing | Not allowed |
| Active borrowing deletion | Restricted |
| Failed login attempts | Limited with temporary lockout |

These settings can be adjusted through the project's configuration file.

---

## 🗄️ Database

The application uses **SQLite3** as its database system.

The database contains tables for:

- Administrators
- Members
- Authors
- Categories
- Publishers
- Books
- Borrowings
- Fines
- Reservations

Foreign key relationships are used to maintain connections between related records.

---

## 🔐 Security

The system includes several security measures:

- Passwords are stored using secure hashing rather than plain text.
- Unique salts are generated for password protection.
- Password input is hidden in the terminal.
- SQL queries use parameters to reduce SQL injection risks.
- Login attempts are monitored to provide temporary protection against repeated failed logins.
- Database operations use transactions where multiple related changes need to happen together.

---

## 📚 Borrowing & Return System

The borrowing system manages the complete book lending process.

When a book is issued:

1. The member's borrowing limit is checked.
2. Book availability is verified.
3. A borrowing record is created.
4. The available book quantity is updated.
5. A due date is assigned automatically.

When a book is returned:

1. The borrowing record is updated.
2. The return date is recorded.
3. Book availability is updated.
4. Any applicable overdue fine is calculated.

---

## 💰 Fine Management

The system automatically calculates fines for overdue books.

The default fine rate is:

```text
Rs. 20 per overdue day
```

The calculation is based on the number of overdue days and uses Python's `Decimal` type for accurate financial calculations.

---

## 📌 Reservation System

Members can reserve books through the system.

The reservation module manages:

- Creating reservations
- Reservation status
- Reservation queues
- Book availability
- Reservation fulfillment

---

## 📊 Reports & CSV Export

The system provides reporting functionality for important library records.

Reports can be generated for:

- Books
- Members
- Borrowings
- Fines
- Reservations

The generated information can be exported as CSV files for easy viewing and further processing.

---

## 🧪 Testing

The project includes automated tests covering important system functionality.

Run the tests using:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The tests cover areas such as:

- Authentication
- Password validation
- Member registration
- Book management
- Borrowing and returning
- Book quantity management
- Fine calculation
- Renewals
- Reservations
- CSV report generation

---

## 🔮 Future Improvements

Possible future improvements include:

- 🌐 Web-based interface
- 📱 Mobile application
- 🔖 Barcode and RFID support
- 📧 Email notifications for overdue books
- 📩 SMS notifications
- 🏢 Multi-branch library support
- ☁️ Cloud-based database
- 📊 Advanced analytics dashboard

---

## 📄 License

This project is developed as a software engineering and database management project.

Licensed under the **MIT License**.

---

## 👩‍💻 Built By

**Maryam Fahim**
