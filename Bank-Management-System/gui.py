"""Professional desktop GUI for the Bank Management System.

Built with Tkinter/ttk only: no third-party GUI dependency is required.
Includes full admin screens for customers, accounts and transaction
records, plus customer banking operations and profile management.
All actions apply instantly with inline, non-blocking status feedback —
no confirmation pop-ups interrupt the workflow.
"""
from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import ttk
from decimal import Decimal, InvalidOperation
from datetime import datetime

from database import DatabaseManager
from services.auth_service import AuthService
from services.customer_service import CustomerService
from services.account_service import AccountService
from services.transaction_service import TransactionService
from utils.security import hash_password
from config import (
    ACCOUNT_TYPES, ACCOUNT_STATUS_ACTIVE, ACCOUNT_STATUS_FROZEN,
    ACCOUNT_STATUS_CLOSED, CUSTOMER_STATUS_ACTIVE, CUSTOMER_STATUS_BLOCKED,
    MIN_INITIAL_DEPOSIT, CURRENCY_SYMBOL,
)

BG = "#f5f7fb"
NAVY = "#0f1f3d"
NAVY2 = "#162b52"
ACCENT = "#1f8a70"
ACCENT2 = "#2c7be5"
TEXT = "#172033"
MUTED = "#6b778c"
BORDER = "#e3e8f0"
WHITE = "#ffffff"
DANGER = "#d64545"
WARNING = "#d18b16"
SUCCESS = "#1f8a70"


class BankGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maryam Fahim • Bank Management System")
        self.geometry("1360x820")
        self.minsize(1120, 700)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.db = DatabaseManager()
        self.db.seed_demo_data()
        self.auth = AuthService(self.db)
        self.customers = CustomerService(self.db)
        self.accounts = AccountService(self.db)
        self.transactions = TransactionService(self.db)
        self.current_view = None
        self._setup_styles()
        self.show_login()

    # ---------- Styling ----------
    def _setup_styles(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=WHITE)
        s.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("Card.TLabel", background=WHITE, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        s.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 25, "bold"))
        s.configure("CardTitle.TLabel", background=WHITE, foreground=TEXT, font=("Segoe UI", 13, "bold"))
        s.configure("Metric.TLabel", background=WHITE, foreground=TEXT, font=("Segoe UI", 22, "bold"))
        s.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        s.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(15, 9), foreground=WHITE, background=ACCENT)
        s.map("Accent.TButton", background=[("active", "#176b58")])
        s.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8), foreground=WHITE, background=DANGER)
        s.configure("Secondary.TButton", padding=(12, 8), background="#edf1f7")
        s.configure("TEntry", padding=8, font=("Segoe UI", 10))
        s.configure("TCombobox", padding=7, font=("Segoe UI", 10))
        s.configure("Treeview", background=WHITE, fieldbackground=WHITE, foreground=TEXT,
                    rowheight=31, font=("Segoe UI", 9))
        s.configure("Treeview.Heading", background="#eef2f7", foreground=TEXT,
                    font=("Segoe UI", 9, "bold"), padding=8)
        s.map("Treeview", background=[("selected", "#dceee9")], foreground=[("selected", TEXT)])
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", padding=(14, 9), font=("Segoe UI", 9, "bold"))
        s.configure("Status.TLabel", background="#eaf6f2", foreground=SUCCESS, padding=8)

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def card(self, parent, **kw):
        return tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=BORDER, **kw)

    def button(self, parent, text, command, kind="secondary", **kw):
        style = {"accent": "Accent.TButton", "danger": "Danger.TButton", "secondary": "Secondary.TButton"}.get(kind, "TButton")
        return ttk.Button(parent, text=text, command=command, style=style, **kw)

    # ---------- Inline notifications (no popup dialogs) ----------
    def toast(self, message, kind="success"):
        """Show a small, non-blocking banner that fades on its own.
        Replaces messagebox popups so add/edit/delete never interrupt the user."""
        colors = {
            "success": (ACCENT, WHITE, "✓"),
            "error": (DANGER, WHITE, "✕"),
            "warning": (WARNING, WHITE, "!"),
            "info": (ACCENT2, WHITE, "i"),
        }
        bg, fg, icon = colors.get(kind, colors["success"])
        if getattr(self, "_toast", None) is not None:
            try:
                self._toast_job and self.after_cancel(self._toast_job)
            except Exception:
                pass
            try:
                self._toast.destroy()
            except Exception:
                pass
        frame = tk.Frame(self, bg=bg, highlightthickness=0)
        tk.Label(frame, text=f"{icon}  {message}", bg=bg, fg=fg,
                 font=("Segoe UI", 10, "bold"), padx=20, pady=12).pack()
        frame.place(relx=0.5, y=14, anchor="n")
        frame.lift()
        self._toast = frame
        self._toast_job = self.after(3200, self._dismiss_toast)
        return frame

    def _dismiss_toast(self):
        if getattr(self, "_toast", None) is not None:
            try:
                self._toast.destroy()
            except Exception:
                pass
            self._toast = None

    def inline_status(self, parent, **kw):
        """A small label inside a dialog/card for validation feedback that
        appears in place, instead of popping up a separate window."""
        kw.setdefault("bg", WHITE)
        kw.setdefault("fg", DANGER)
        kw.setdefault("font", ("Segoe UI", 9, "bold"))
        kw.setdefault("anchor", "w")
        kw.setdefault("justify", "left")
        kw.setdefault("wraplength", 440)
        lbl = tk.Label(parent, text="", **kw)
        return lbl

    def set_status(self, label, message, ok=False):
        label.configure(text=message, fg=ACCENT if ok else DANGER)

    # ---------- Login / Registration ----------
    def show_login(self):
        self.auth.logout()
        self.clear()
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True)

        left = tk.Frame(root, bg=NAVY, width=455)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="MF", bg=ACCENT, fg=WHITE, font=("Segoe UI", 24, "bold"),
                 width=3, height=1).pack(pady=(115, 22))
        tk.Label(left, text="MARYAM FAHIM", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 26, "bold")).pack()
        tk.Label(left, text="BANK MANAGEMENT SYSTEM", bg=NAVY, fg="#9de0d1",
                 font=("Segoe UI", 13, "bold")).pack(pady=(5, 18))
        tk.Label(left, text="A secure, professional desktop banking platform",
                 bg=NAVY, fg="#b9c4d5", font=("Segoe UI", 11)).pack()
        for text in ("✓ Customer & account management", "✓ Deposits, withdrawals & transfers", "✓ Reports & transaction history"):
            tk.Label(left, text=text, bg=NAVY, fg="#dbe2ed", font=("Segoe UI", 10), anchor="w").pack(fill="x", padx=82, pady=8)
        tk.Label(left, text="Version 3.0 • Desktop Edition", bg=NAVY, fg="#75839b",
                 font=("Segoe UI", 9)).pack(side="bottom", pady=35)

        right = tk.Frame(root, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        box = self.card(right)
        box.place(relx=.5, rely=.5, anchor="center", width=535, height=570)

        tk.Label(box, text="Welcome back", bg=WHITE, fg=TEXT, font=("Segoe UI", 27, "bold")).pack(pady=(48, 5))
        tk.Label(box, text="Sign in to continue to your banking dashboard", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 10)).pack(pady=(0, 28))
        self.login_role = tk.StringVar(value="Customer")
        role = tk.Frame(box, bg=WHITE)
        role.pack(pady=(0, 18))
        for value in ("Customer", "Admin"):
            ttk.Radiobutton(role, text=value, variable=self.login_role, value=value).pack(side="left", padx=28)

        self.login_user = self.field(box, "Username")
        self.login_pass = self.field(box, "Password", show="•")
        self.login_pass.bind("<Return>", lambda e: self.do_login())
        self.login_status = self.inline_status(box, bg=WHITE)
        self.login_status.pack(fill="x", padx=72, pady=(0, 6))
        self.button(box, "SIGN IN", self.do_login, "accent").pack(fill="x", padx=72, pady=(8, 9))
        self.button(box, "Create new customer account", self.show_register).pack(fill="x", padx=72)
        tk.Label(box, text="Maryam Fahim demo access\nCustomer: maryam_fahim / Maryam@123\nAdmin: maryam_admin / Maryam@Admin123",
                 bg=WHITE, fg="#8793a6", font=("Segoe UI", 9), justify="center").pack(pady=19)

    def field(self, parent, label, textvariable=None, show=""):
        tk.Label(parent, text=label, bg=WHITE, fg=TEXT, font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=72, pady=(5, 4))
        e = ttk.Entry(parent, textvariable=textvariable, show=show)
        e.pack(fill="x", padx=72, pady=(0, 10))
        return e

    def do_login(self):
        u, p = self.login_user.get().strip(), self.login_pass.get()
        if not u or not p:
            self.set_status(self.login_status, "Enter username and password.")
            return
        if self.login_role.get() == "Admin":
            ok, msg, data = self.auth.login_admin(u, p)
            if ok:
                self.show_admin()
            else:
                self.set_status(self.login_status, msg)
        else:
            ok, msg, data = self.auth.login_customer(u, p)
            if ok:
                self.customer = data
                self.show_customer()
            else:
                self.set_status(self.login_status, msg)

    def show_register(self):
        self.clear()
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=35, pady=25)
        self.button(top, "← Back to login", self.show_login).pack(side="left")
        tk.Label(top, text="Create Customer", bg=BG, fg=TEXT, font=("Segoe UI", 24, "bold")).pack(side="left", padx=22)
        body = self.card(self, padx=28, pady=24)
        body.pack(fill="both", expand=True, padx=65, pady=(0, 40))
        fields = [("Full Name", "full_name"), ("CNIC", "cnic"), ("Phone", "phone"), ("Email", "email"),
                  ("Address", "address"), ("Date of Birth (YYYY-MM-DD)", "dob"), ("Username", "username"), ("Password", "password")]
        self.reg_vars = {k: tk.StringVar() for _, k in fields}
        for i, (label, key) in enumerate(fields):
            r, c = divmod(i, 2)
            tk.Label(body, text=label, bg=WHITE, fg=TEXT, font=("Segoe UI", 10, "bold"), anchor="w").grid(row=r*2, column=c, sticky="w", padx=14, pady=(5, 4))
            ttk.Entry(body, textvariable=self.reg_vars[key], show="•" if key == "password" else "").grid(row=r*2+1, column=c, sticky="ew", padx=14, pady=(0, 13))
        body.columnconfigure(0, weight=1); body.columnconfigure(1, weight=1)
        self.reg_status = self.inline_status(body)
        self.reg_status.grid(row=8, column=0, columnspan=2, sticky="w", padx=14)
        self.button(body, "CREATE CUSTOMER", self.register_customer, "accent").grid(row=9, column=0, columnspan=2, pady=18)

    def register_customer(self):
        v = self.reg_vars
        if not all(x.get().strip() for x in v.values()):
            self.set_status(self.reg_status, "Please complete every field.")
            return
        ok, msg, cid = self.customers.register_customer(v["full_name"].get(), v["cnic"].get(), v["phone"].get(),
            v["email"].get(), v["address"].get(), v["dob"].get(), v["username"].get(), v["password"].get())
        if ok:
            self.show_login()
            self.toast(f"Customer created successfully — ID {cid}.", "success")
        else:
            self.set_status(self.reg_status, msg)

    # ---------- Common application shell ----------
    def shell(self, role, name):
        self.clear()
        self.sidebar = tk.Frame(self, bg=NAVY, width=245)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="MF", bg=ACCENT, fg=WHITE, font=("Segoe UI", 18, "bold"), width=3).pack(pady=(27, 8))
        tk.Label(self.sidebar, text="MARYAM FAHIM", bg=NAVY, fg=WHITE, font=("Segoe UI", 15, "bold")).pack()
        tk.Label(self.sidebar, text="BANKING PLATFORM", bg=NAVY, fg="#8ea0ba", font=("Segoe UI", 8, "bold")).pack(pady=(2, 25))
        self.nav_buttons = []
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.topbar = tk.Frame(self.content, bg=WHITE, height=72, highlightthickness=1, highlightbackground=BORDER)
        self.topbar.pack(fill="x")
        tk.Label(self.topbar, text=name, bg=WHITE, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(side="left", padx=28, pady=20)
        tk.Label(self.topbar, text=role, bg="#eaf6f2", fg=SUCCESS, font=("Segoe UI", 9, "bold"), padx=10, pady=5).pack(side="left")
        self.button(self.topbar, "Logout", self.show_login).pack(side="right", padx=22)
        self.page = tk.Frame(self.content, bg=BG)
        self.page.pack(fill="both", expand=True, padx=24, pady=22)

    def nav(self, text, command):
        b = tk.Button(self.sidebar, text="  " + text, command=command, anchor="w", relief="flat", bd=0,
                      bg=NAVY, fg="#d5deea", activebackground=NAVY2, activeforeground=WHITE,
                      font=("Segoe UI", 10, "bold"), padx=18, pady=11, cursor="hand2")
        b.pack(fill="x", padx=12, pady=2)
        self.nav_buttons.append(b)
        return b

    def page_title(self, title, subtitle=""):
        for w in self.page.winfo_children(): w.destroy()
        tk.Label(self.page, text=title, bg=BG, fg=TEXT, font=("Segoe UI", 25, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(self.page, text=subtitle, bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 18))
        return self.page

    def make_tree(self, parent, columns, widths=None, height=14):
        wrap = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)
        wrap.pack(fill="both", expand=True)
        ids = [c[0] for c in columns]
        tree = ttk.Treeview(wrap, columns=ids, show="headings", height=height)
        for i, (key, heading) in enumerate(columns):
            tree.heading(key, text=heading)
            tree.column(key, width=(widths[i] if widths else 120), anchor="w")
        y = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        x = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y.set, xscrollcommand=x.set)
        tree.grid(row=0, column=0, sticky="nsew"); y.grid(row=0, column=1, sticky="ns"); x.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1); wrap.columnconfigure(0, weight=1)
        return tree

    def metric(self, parent, label, value):
        c = self.card(parent, padx=18, pady=15)
        c.pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(c, text=label.upper(), bg=WHITE, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(c, text=value, bg=WHITE, fg=TEXT, font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=(6, 0))

    def selected_id(self, tree):
        sel = tree.selection()
        if not sel:
            self.toast("Select a row first.", "warning")
            return None
        return tree.item(sel[0], "values")[0]

    # ---------- Admin ----------
    def show_admin(self):
        self.shell("ADMINISTRATOR", self.auth.current_user["full_name"])
        self.nav("Dashboard", self.admin_dashboard)
        self.nav("Customers", self.admin_customers)
        self.nav("Accounts", self.admin_accounts)
        self.nav("Transactions", self.admin_transactions)
        self.nav("Reports", self.admin_reports)
        self.nav("Admin Profile", self.admin_profile)
        tk.Label(self.sidebar, text="Full administrative access", bg=NAVY, fg="#7486a2",
                 font=("Segoe UI", 8), justify="left").pack(side="bottom", padx=25, pady=30, anchor="w")
        self.admin_dashboard()

    def admin_dashboard(self):
        self.page_title("Dashboard", "Bank-wide overview and quick actions")
        conn = self.db.get_connection()
        try:
            c = conn.cursor()
            customers = c.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
            active_c = c.execute("SELECT COUNT(*) FROM customers WHERE status='Active'").fetchone()[0]
            accounts = c.execute("SELECT COUNT(*) FROM accounts WHERE status!='Closed'").fetchone()[0]
            balance = c.execute("SELECT COALESCE(SUM(CAST(balance AS REAL)),0) FROM accounts WHERE status!='Closed'").fetchone()[0]
            txns = c.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        finally: conn.close()
        metrics = tk.Frame(self.page, bg=BG); metrics.pack(fill="x", pady=(0, 20))
        for l,v in (("Customers",customers),("Active Customers",active_c),("Active Accounts",accounts),("Total Deposits",f"Rs. {balance:,.0f}"),("Transactions",txns)):
            self.metric(metrics,l,v)
        actions = self.card(self.page, padx=22, pady=20); actions.pack(fill="x", pady=(0,18))
        tk.Label(actions,text="Quick actions",bg=WHITE,fg=TEXT,font=("Segoe UI",14,"bold")).pack(anchor="w")
        row=tk.Frame(actions,bg=WHITE); row.pack(anchor="w",pady=(14,0))
        for t,cmd in (("＋ New Customer",self.new_customer_dialog),("＋ New Account",self.new_account_dialog),("↻ Refresh",self.admin_dashboard)):
            self.button(row,t,cmd,"accent" if "New" in t else "secondary").pack(side="left",padx=(0,10))
        recent=self.card(self.page,padx=18,pady=16); recent.pack(fill="both",expand=True)
        tk.Label(recent,text="Recent transactions",bg=WHITE,fg=TEXT,font=("Segoe UI",13,"bold")).pack(anchor="w",pady=(0,10))
        tree=self.make_tree(recent,[("id","ID"),("txn","Transaction"),("acc","Account"),("type","Type"),("amount","Amount"),("date","Date"),("status","Status")],[40,180,110,145,120,150,100],8)
        conn=self.db.get_connection(); rows=conn.execute("SELECT id,transaction_id,account_id,transaction_type,amount,transaction_date,status FROM transactions ORDER BY id DESC LIMIT 12").fetchall(); conn.close()
        for r in rows: tree.insert("", "end", values=(r[0],r[1],r[2],r[3],f"Rs. {Decimal(str(r[4])):,.2f}",r[5],r[6]))

    def toolbar(self,parent, search_var, search_cmd, add_cmd, refresh_cmd, add_text="＋ Add"):
        bar=tk.Frame(parent,bg=BG); bar.pack(fill="x",pady=(0,12))
        ttk.Entry(bar,textvariable=search_var,width=34).pack(side="left")
        self.button(bar,"Search",search_cmd,"accent").pack(side="left",padx=7)
        self.button(bar,"Refresh",refresh_cmd).pack(side="left")
        self.button(bar,add_text,add_cmd,"accent").pack(side="right")
        return bar

    def admin_customers(self):
        p=self.page_title("Customers", "Create, view, edit, control status and safely delete customer records")
        self.cust_search=tk.StringVar()
        self.toolbar(p,self.cust_search,self.refresh_customers,self.new_customer_dialog,self.admin_customers)
        tree=self.make_tree(p,[("id","ID"),("name","Full Name"),("cnic","CNIC"),("phone","Phone"),("email","Email"),("user","Username"),("status","Status"),("created","Created")],[45,170,135,115,210,130,90,145],12)
        self.cust_tree=tree
        self.refresh_customers()
        actions=tk.Frame(p,bg=BG); actions.pack(fill="x",pady=(10,0))
        for t,cmd,kind in (("Edit Customer",self.edit_customer_dialog,"secondary"),("Block / Unblock",self.toggle_customer,"secondary"),("Delete Customer",self.delete_customer,"danger")):
            self.button(actions,t,cmd,kind).pack(side="left",padx=(0,8))

    def refresh_customers(self):
        if not hasattr(self,'cust_tree'): return
        for x in self.cust_tree.get_children(): self.cust_tree.delete(x)
        rows=self.customers.search_customers(self.cust_search.get() if hasattr(self,'cust_search') else "")
        for c in rows:
            self.cust_tree.insert("","end",values=(c.id,c.full_name,c.cnic,c.phone,c.email,c.username,c.status,c.created_at))

    def new_customer_dialog(self): self.customer_dialog()

    def customer_dialog(self, customer=None):
        win=tk.Toplevel(self); win.title("Edit Customer" if customer else "New Customer"); win.geometry("680x700"); win.configure(bg=BG); win.transient(self); win.grab_set()
        tk.Label(win,text="Edit Customer" if customer else "Create Customer",bg=BG,fg=TEXT,font=("Segoe UI",20,"bold")).pack(anchor="w",padx=28,pady=(24,3))
        tk.Label(win,text="Customer master data",bg=BG,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=28,pady=(0,15))
        card=self.card(win,padx=22,pady=20); card.pack(fill="both",expand=True,padx=25,pady=(0,25))
        fields=[("Full Name","full_name"),("CNIC","cnic"),("Phone","phone"),("Email","email"),("Address","address"),("Date of Birth","dob"),("Username","username")]
        vars={k:tk.StringVar(value=getattr(customer,k,"") if customer else "") for _,k in fields}
        for i,(lab,key) in enumerate(fields):
            r,c=divmod(i,2)
            tk.Label(card,text=lab,bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).grid(row=r*2,column=c,sticky="w",padx=8,pady=(3,3))
            ttk.Entry(card,textvariable=vars[key],state="disabled" if customer and key in ("username",) else "normal").grid(row=r*2+1,column=c,sticky="ew",padx=8,pady=(0,11))
        card.columnconfigure(0,weight=1);card.columnconfigure(1,weight=1)
        pw=tk.StringVar()
        if not customer:
            tk.Label(card,text="Set Login Password",bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).grid(row=8,column=0,sticky="w",padx=8,pady=(3,3))
            ttk.Entry(card,textvariable=pw,show="•").grid(row=9,column=0,sticky="ew",padx=8,pady=(0,11))
        status=self.inline_status(card)
        status.grid(row=10,column=0,columnspan=2,sticky="w",padx=8,pady=(2,0))
        def save():
            vals={k:v.get().strip() for k,v in vars.items()}
            if not all(vals.values()): self.set_status(status,"Complete all fields.");return
            if customer:
                ok,msg=self.update_customer_full(customer.id,vals)
            else:
                if not pw.get().strip(): self.set_status(status,"Set a login password.");return
                ok,msg,_=self.customers.register_customer(vals['full_name'],vals['cnic'],vals['phone'],vals['email'],vals['address'],vals['dob'],vals['username'],pw.get().strip())
            if ok:
                win.destroy();self.refresh_customers();self.toast(msg,"success")
            else: self.set_status(status,msg)
        self.button(card,"SAVE CUSTOMER",save,"accent").grid(row=11,column=0,columnspan=2,pady=15)

    def update_customer_full(self,cid,vals):
        conn=self.db.get_connection()
        try:
            cur=conn.cursor()
            cur.execute("SELECT id FROM customers WHERE lower(email)=? AND id!=?",(vals['email'].lower(),cid))
            if cur.fetchone(): return False,"Email is already used by another customer."
            cur.execute("SELECT id FROM customers WHERE cnic=? AND id!=?",(vals['cnic'],cid))
            if cur.fetchone(): return False,"CNIC is already used by another customer."
            cur.execute("UPDATE customers SET full_name=?,cnic=?,phone=?,email=?,address=?,date_of_birth=? WHERE id=?",
                        (vals['full_name'],vals['cnic'],vals['phone'],vals['email'].lower(),vals['address'],vals['dob'],cid))
            conn.commit();return True,"Customer updated successfully."
        except Exception as e: conn.rollback();return False,str(e)
        finally: conn.close()

    def edit_customer_dialog(self):
        cid=self.selected_id(self.cust_tree)
        if cid:
            c=self.customers.get_customer_by_id(int(cid)); self.customer_dialog(c)

    def toggle_customer(self):
        cid=self.selected_id(self.cust_tree)
        if not cid:return
        c=self.customers.get_customer_by_id(int(cid)); new=CUSTOMER_STATUS_BLOCKED if c.status==CUSTOMER_STATUS_ACTIVE else CUSTOMER_STATUS_ACTIVE
        ok,msg=self.customers.set_customer_status(c.id,new)
        if ok:self.refresh_customers();self.toast(f"{c.full_name} is now {new}.","success")
        else:self.toast(msg,"error")

    def delete_customer(self):
        cid=self.selected_id(self.cust_tree)
        if not cid:return
        c=self.customers.get_customer_by_id(int(cid))
        ok,msg=self.customers.delete_customer(c.id)
        if ok:self.refresh_customers();self.toast(msg,"success")
        else:self.toast(msg,"error")

    # ---------- Accounts ----------
    def admin_accounts(self):
        p=self.page_title("Accounts", "Create, edit, freeze and close accounts with safe financial rules")
        self.acc_search=tk.StringVar(); self.toolbar(p,self.acc_search,self.refresh_accounts,self.new_account_dialog,self.admin_accounts)
        tree=self.make_tree(p,[("id","ID"),("number","Account No."),("cid","Customer ID"),("name","Customer"),("type","Type"),("balance","Balance"),("status","Status"),("created","Created")],[45,120,90,170,100,130,90,150],12); self.acc_tree=tree;self.refresh_accounts()
        actions=tk.Frame(p,bg=BG);actions.pack(fill="x",pady=(10,0))
        for t,cmd,k in (("Edit Account",self.edit_account_dialog,"secondary"),("Freeze / Unfreeze",self.toggle_account,"secondary"),("Close Account",self.close_account,"secondary"),("Delete Account",self.delete_account,"danger")):
            self.button(actions,t,cmd,k).pack(side="left",padx=(0,8))

    def refresh_accounts(self):
        if not hasattr(self,'acc_tree'):return
        for x in self.acc_tree.get_children():self.acc_tree.delete(x)
        rows=self.accounts.search_accounts(self.acc_search.get() if hasattr(self,'acc_search') else "")
        for r in rows:self.acc_tree.insert("","end",values=(r['id'],r['account_number'],r['customer_id'],r['customer_name'],r['account_type'],f"Rs. {Decimal(str(r['balance'])):,.2f}",r['status'],r['created_at']))

    def new_account_dialog(self):self.account_dialog()

    def account_dialog(self,account=None):
        win=tk.Toplevel(self);win.title("Edit Account" if account else "New Account");win.geometry("540x410");win.configure(bg=BG);win.transient(self);win.grab_set()
        tk.Label(win,text="Edit Account" if account else "Create Account",bg=BG,fg=TEXT,font=("Segoe UI",20,"bold")).pack(anchor="w",padx=25,pady=(22,3))
        card=self.card(win,padx=22,pady=20);card.pack(fill="both",expand=True,padx=22,pady=18)
        cust=tk.StringVar(value=str(account.customer_id) if account else "")
        typ=tk.StringVar(value=account.account_type if account else ACCOUNT_TYPES[0])
        dep=tk.StringVar(value="" if account else "1000")
        tk.Label(card,text="Customer ID",bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w")
        ttk.Entry(card,textvariable=cust,state="disabled" if account else "normal").pack(fill="x",pady=(3,12))
        tk.Label(card,text="Account Type",bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w")
        ttk.Combobox(card,textvariable=typ,values=ACCOUNT_TYPES,state="readonly").pack(fill="x",pady=(3,12))
        if not account:
            tk.Label(card,text=f"Initial Deposit (minimum {CURRENCY_SYMBOL} {MIN_INITIAL_DEPOSIT})",bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w")
            ttk.Entry(card,textvariable=dep).pack(fill="x",pady=(3,15))
        status=self.inline_status(card);status.pack(fill="x",pady=(0,4))
        def save():
            try:cid=int(cust.get())
            except:self.set_status(status,"Customer ID must be numeric.");return
            if account:
                conn=self.db.get_connection()
                try:
                    conn.execute("UPDATE accounts SET account_type=? WHERE id=?",(typ.get(),account.id));conn.commit()
                    ok,msg=True,"Account updated successfully."
                except Exception as e:conn.rollback();ok,msg=False,str(e)
                finally:conn.close()
            else:
                try:amount=Decimal(dep.get()).quantize(Decimal("0.01"))
                except InvalidOperation:self.set_status(status,"Enter a valid deposit amount.");return
                ok,msg,_=self.accounts.create_account(cid,typ.get(),amount)
            if ok:win.destroy();self.refresh_accounts();self.toast(msg,"success")
            else:self.set_status(status,msg)
        self.button(card,"SAVE ACCOUNT",save,"accent").pack(fill="x",pady=8)

    def edit_account_dialog(self):
        aid=self.selected_id(self.acc_tree)
        if aid:
            a=self.accounts.get_account_by_id(int(aid));self.account_dialog(a)

    def toggle_account(self):
        aid=self.selected_id(self.acc_tree)
        if not aid:return
        a=self.accounts.get_account_by_id(int(aid))
        if a.status==ACCOUNT_STATUS_ACTIVE:ok,msg=self.accounts.freeze_account(a.account_number)
        elif a.status==ACCOUNT_STATUS_FROZEN:ok,msg=self.accounts.unfreeze_account(a.account_number)
        else:ok,msg=False,"Closed accounts cannot be unfrozen."
        if ok:self.refresh_accounts();self.toast(msg,"success")
        else:self.toast(msg,"error")

    def close_account(self):
        aid=self.selected_id(self.acc_tree)
        if not aid:return
        a=self.accounts.get_account_by_id(int(aid))
        ok,msg=self.accounts.close_account(a.account_number)
        if ok:self.refresh_accounts();self.toast(msg,"success")
        else:self.toast(msg,"error")

    def delete_account(self):
        aid=self.selected_id(self.acc_tree)
        if not aid:return
        a=self.accounts.get_account_by_id(int(aid))
        conn=self.db.get_connection()
        try:
            row=conn.execute("SELECT balance,status FROM accounts WHERE id=?",(a.id,)).fetchone()
            if not row:return
            if row[1]!=ACCOUNT_STATUS_CLOSED or Decimal(str(row[0]))!=Decimal("0.00"):
                self.toast("Account must be CLOSED and have a zero balance to delete.","warning");return
            conn.execute("DELETE FROM transactions WHERE account_id=?",(a.id,));conn.execute("DELETE FROM accounts WHERE id=?",(a.id,));conn.commit();self.refresh_accounts();self.toast("Account deleted successfully.","success")
        except Exception as e:conn.rollback();self.toast(str(e),"error")
        finally:conn.close()

    # ---------- Transactions ----------
    def admin_transactions(self):
        p=self.page_title("Transactions", "View all activity, post transactions, edit descriptions and safely remove failed records")
        self.tx_search=tk.StringVar(); self.toolbar(p,self.tx_search,self.refresh_transactions,self.transaction_create_dialog,self.admin_transactions,"＋ New Transaction")
        tree=self.make_tree(p,[("id","ID"),("txn","Transaction ID"),("acc","Account"),("type","Type"),("amount","Amount"),("before","Before"),("after","After"),("desc","Description"),("date","Date"),("status","Status")],[45,170,100,130,120,120,120,240,150,100],12);self.tx_tree=tree;self.refresh_transactions()
        actions=tk.Frame(p,bg=BG);actions.pack(fill="x",pady=(10,0))
        self.button(actions,"Edit Description",self.edit_transaction_dialog).pack(side="left",padx=(0,8))
        self.button(actions,"Delete Failed Record",self.delete_transaction,"danger").pack(side="left")

    def refresh_transactions(self):
        if not hasattr(self,'tx_tree'):return
        for x in self.tx_tree.get_children():self.tx_tree.delete(x)
        q=self.tx_search.get().strip() if hasattr(self,'tx_search') else ""
        conn=self.db.get_connection()
        sql="""SELECT t.id,t.transaction_id,a.account_number,t.transaction_type,t.amount,t.balance_before,t.balance_after,t.description,t.transaction_date,t.status
               FROM transactions t JOIN accounts a ON a.id=t.account_id
               WHERE lower(t.transaction_id) LIKE ? OR lower(a.account_number) LIKE ? OR lower(t.transaction_type) LIKE ? OR lower(COALESCE(t.description,'')) LIKE ?
               ORDER BY t.id DESC"""
        like=f"%{q.lower()}%";rows=conn.execute(sql,(like,like,like,like)).fetchall();conn.close()
        for r in rows:self.tx_tree.insert("","end",values=(r[0],r[1],r[2],r[3],f"Rs. {Decimal(str(r[4])):,.2f}",f"Rs. {Decimal(str(r[5])):,.2f}",f"Rs. {Decimal(str(r[6])):,.2f}",r[7] or "",r[8],r[9]))

    def transaction_create_dialog(self):
        win=tk.Toplevel(self);win.title("New Transaction");win.geometry("520x500");win.configure(bg=BG);win.transient(self);win.grab_set()
        tk.Label(win,text="Create Transaction",bg=BG,fg=TEXT,font=("Segoe UI",20,"bold")).pack(anchor="w",padx=25,pady=(22,3))
        card=self.card(win,padx=22,pady=18);card.pack(fill="both",expand=True,padx=22,pady=18)
        typ=tk.StringVar(value="Deposit");acc=tk.StringVar();amt=tk.StringVar();desc=tk.StringVar();related=tk.StringVar()
        for label,var,values in (("Transaction Type",typ,["Deposit","Withdrawal","Transfer"]),("Account Number",acc,None),("Amount",amt,None),("Description",desc,None),("Related Account (for transfer)",related,None)):
            tk.Label(card,text=label,bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(3,3))
            if values:ttk.Combobox(card,textvariable=var,values=values,state="readonly").pack(fill="x",pady=(0,10))
            else:ttk.Entry(card,textvariable=var).pack(fill="x",pady=(0,10))
        status=self.inline_status(card);status.pack(fill="x",pady=(0,4))
        def save():
            try:a=Decimal(amt.get()).quantize(Decimal("0.01"))
            except InvalidOperation:self.set_status(status,"Enter a valid amount.");return
            if typ.get()=="Deposit":ok,msg=self.transactions.deposit(acc.get(),a,desc.get() or "Admin deposit")
            elif typ.get()=="Withdrawal":ok,msg=self.transactions.withdraw(acc.get(),a,desc.get() or "Admin withdrawal")
            else:ok,msg=self.transactions.transfer(acc.get(),related.get(),a,desc.get() or "Admin transfer")
            if ok:win.destroy();self.refresh_transactions();self.toast(msg,"success")
            else:self.set_status(status,msg)
        self.button(card,"POST TRANSACTION",save,"accent").pack(fill="x",pady=8)

    def edit_transaction_dialog(self):
        tid=self.selected_id(self.tx_tree)
        if not tid:return
        conn=self.db.get_connection();r=conn.execute("SELECT description FROM transactions WHERE id=?",(tid,)).fetchone();conn.close()
        if not r:return
        win=tk.Toplevel(self);win.title("Edit Transaction Description");win.geometry("460x250");win.configure(bg=BG);win.transient(self);win.grab_set()
        card=self.card(win,padx=22,pady=20);card.pack(fill="both",expand=True,padx=22,pady=22)
        var=tk.StringVar(value=r[0] or "");tk.Label(card,text="Description",bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w");ttk.Entry(card,textvariable=var).pack(fill="x",pady=8)
        def save():
            conn=self.db.get_connection();conn.execute("UPDATE transactions SET description=? WHERE id=?",(var.get().strip(),tid));conn.commit();conn.close();win.destroy();self.refresh_transactions();self.toast("Description updated.","success")
        self.button(card,"UPDATE DESCRIPTION",save,"accent").pack(fill="x",pady=10)

    def delete_transaction(self):
        tid=self.selected_id(self.tx_tree)
        if not tid:return
        conn=self.db.get_connection();r=conn.execute("SELECT status FROM transactions WHERE id=?",(tid,)).fetchone();conn.close()
        if not r:return
        if r[0]!="Failed":self.toast("Completed transactions are protected and cannot be deleted. Only Failed records may be removed.","warning");return
        conn=self.db.get_connection();conn.execute("DELETE FROM transactions WHERE id=?",(tid,));conn.commit();conn.close();self.refresh_transactions();self.toast("Transaction record deleted.","success")

    # ---------- Reports ----------
    def admin_reports(self):
        p=self.page_title("Reports", "Export current bank data to CSV files")
        card=self.card(p,padx=25,pady=25);card.pack(fill="x")
        tk.Label(card,text="Management reports",bg=WHITE,fg=TEXT,font=("Segoe UI",15,"bold")).pack(anchor="w")
        tk.Label(card,text="Generate fresh CSV files from the current database.",bg=WHITE,fg=MUTED).pack(anchor="w",pady=(4,18))
        row=tk.Frame(card,bg=WHITE);row.pack(anchor="w")
        self.button(row,"Export Customers",lambda:self.export_csv("customers")).pack(side="left",padx=(0,8))
        self.button(row,"Export Accounts",lambda:self.export_csv("accounts")).pack(side="left",padx=(0,8))
        self.button(row,"Export Transactions",lambda:self.export_csv("transactions")).pack(side="left")
        tk.Label(p,text="Files are saved inside the project's exported_reports folder.",bg=BG,fg=MUTED).pack(anchor="w",pady=15)

    def export_csv(self,kind):
        from pathlib import Path
        import csv
        out=Path(__file__).resolve().parent/"exported_reports";out.mkdir(exist_ok=True)
        conn=self.db.get_connection()
        queries={
          "customers":("SELECT id,full_name,cnic,phone,email,address,date_of_birth,username,status,created_at FROM customers",out/"customers.csv"),
          "accounts":("SELECT a.id,a.account_number,a.customer_id,c.full_name,a.account_type,a.balance,a.status,a.created_at,a.closed_at FROM accounts a JOIN customers c ON c.id=a.customer_id",out/"accounts.csv"),
          "transactions":("SELECT t.id,t.transaction_id,a.account_number,t.transaction_type,t.amount,t.balance_before,t.balance_after,t.description,t.related_account,t.transaction_date,t.status FROM transactions t JOIN accounts a ON a.id=t.account_id",out/"transactions.csv")}
        sql,path=queries[kind];rows=conn.execute(sql).fetchall();headers=[d[0] for d in conn.execute(sql).description];conn.close()
        with path.open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f);w.writerow(headers);w.writerows(rows)
        self.toast(f"Saved {len(rows)} records to {path.name}.","success")

    def admin_profile(self):
        p=self.page_title("Admin Profile", "Administrator account")
        card=self.card(p,padx=25,pady=25);card.pack(fill="x")
        a=self.auth.current_user
        for lab,val in (("Name",a['full_name']),("Username",a['username']),("Email",a['email']),("Role","Administrator")):
            row=tk.Frame(card,bg=WHITE);row.pack(fill="x",pady=7);tk.Label(row,text=lab,bg=WHITE,fg=MUTED,width=16,anchor="w").pack(side="left");tk.Label(row,text=val,bg=WHITE,fg=TEXT,font=("Segoe UI",10,"bold")).pack(side="left")

    # ---------- Customer ----------
    def show_customer(self):
        self.customer=self.customers.get_customer_by_id(self.customer.id)
        self.shell("CUSTOMER", self.customer.full_name)
        self.nav("Overview", self.customer_overview)
        self.nav("My Accounts", self.customer_accounts)
        self.nav("Deposit", self.deposit_page)
        self.nav("Withdraw", self.withdraw_page)
        self.nav("Transfer", self.transfer_page)
        self.nav("Transactions", self.customer_transactions)
        self.nav("Profile & Password", self.customer_profile)
        tk.Label(self.sidebar,text="Secure customer portal",bg=NAVY,fg="#7486a2",font=("Segoe UI",9)).pack(side="bottom",pady=35)
        self.customer_overview()

    def customer_overview(self):
        p=self.page_title("Good day, " + self.customer.full_name.split()[0], "Your personal banking snapshot")
        accounts=self.accounts.get_accounts_by_customer_id(self.customer.id,include_closed=False)
        total=sum((a.balance for a in accounts),Decimal("0"))
        m=tk.Frame(p,bg=BG);m.pack(fill="x",pady=(0,20))
        for l,v in (("Total balance",f"Rs. {total:,.2f}"),("Active accounts",len(accounts)),("Customer ID",self.customer.id)):
            self.metric(m,l,v)
        c=self.card(p,padx=20,pady=18);c.pack(fill="both",expand=True)
        tk.Label(c,text="Your accounts",bg=WHITE,fg=TEXT,font=("Segoe UI",14,"bold")).pack(anchor="w",pady=(0,10))
        tree=self.make_tree(c,[("num","Account Number"),("type","Type"),("bal","Balance"),("status","Status"),("created","Opened")],[180,130,170,110,170],8)
        for a in accounts:tree.insert("","end",values=(a.account_number,a.account_type,f"Rs. {a.balance:,.2f}",a.status,a.created_at))

    def customer_accounts(self):
        p=self.page_title("My Accounts", "Create and manage your own bank accounts")
        self.button(p,"＋ Open New Account",self.customer_open_account,"accent").pack(anchor="e",pady=(0,12))
        tree=self.make_tree(p,[("id","ID"),("num","Account Number"),("type","Type"),("bal","Balance"),("status","Status"),("created","Created")],[50,190,140,170,110,170],13)
        for a in self.accounts.get_accounts_by_customer_id(self.customer.id,include_closed=True):tree.insert("","end",values=(a.id,a.account_number,a.account_type,f"Rs. {a.balance:,.2f}",a.status,a.created_at))

    def customer_open_account(self):
        self.account_dialog_customer()

    def account_dialog_customer(self):
        win=tk.Toplevel(self);win.title("Open Account");win.geometry("450x350");win.configure(bg=BG);win.transient(self);win.grab_set()
        card=self.card(win,padx=25,pady=24);card.pack(fill="both",expand=True,padx=22,pady=22)
        typ=tk.StringVar(value=ACCOUNT_TYPES[0]);dep=tk.StringVar(value="1000")
        tk.Label(card,text="Open a new account",bg=WHITE,fg=TEXT,font=("Segoe UI",18,"bold")).pack(anchor="w",pady=(0,15))
        tk.Label(card,text="Account type",bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w");ttk.Combobox(card,textvariable=typ,values=ACCOUNT_TYPES,state="readonly").pack(fill="x",pady=(4,12))
        tk.Label(card,text=f"Initial deposit (minimum Rs. {MIN_INITIAL_DEPOSIT})",bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w");ttk.Entry(card,textvariable=dep).pack(fill="x",pady=(4,15))
        status=self.inline_status(card);status.pack(fill="x",pady=(0,6))
        def save():
            try:a=Decimal(dep.get()).quantize(Decimal("0.01"))
            except InvalidOperation:self.set_status(status,"Enter a valid amount.");return
            ok,msg,_=self.accounts.create_account(self.customer.id,typ.get(),a)
            if ok:win.destroy();self.customer_accounts();self.toast(msg,"success")
            else:self.set_status(status,msg)
        self.button(card,"OPEN ACCOUNT",save,"accent").pack(fill="x")

    def transaction_form(self,title,kind):
        p=self.page_title(title,"Fast, secure banking transaction")
        card=self.card(p,padx=30,pady=24);card.pack(fill="x")
        accounts=[a for a in self.accounts.get_accounts_by_customer_id(self.customer.id,include_closed=False)]
        nums=[a.account_number for a in accounts]
        acc=tk.StringVar(value=nums[0] if nums else "");amt=tk.StringVar();desc=tk.StringVar()
        for lab,var in (("Account",acc),("Amount (Rs.)",amt),("Description",desc)):
            tk.Label(card,text=lab,bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(3,3))
            if lab=="Account":ttk.Combobox(card,textvariable=var,values=nums,state="readonly").pack(fill="x",pady=(0,13))
            else:ttk.Entry(card,textvariable=var).pack(fill="x",pady=(0,13))
        status=self.inline_status(card);status.pack(fill="x",pady=(0,6))
        def submit():
            if not acc.get():self.set_status(status,"Open an account first.");return
            try:a=Decimal(amt.get()).quantize(Decimal("0.01"))
            except InvalidOperation:self.set_status(status,"Enter a valid amount.");return
            if kind=="Deposit":ok,msg=self.transactions.deposit(acc.get(),a,desc.get() or "Customer deposit")
            else:ok,msg=self.transactions.withdraw(acc.get(),a,desc.get() or "Customer withdrawal")
            if ok:self.toast(msg,"success");self.customer_overview()
            else:self.set_status(status,msg)
        self.button(card,f"CONFIRM {kind.upper()}",submit,"accent").pack(anchor="w",pady=5)

    def deposit_page(self):self.transaction_form("Deposit Money","Deposit")
    def withdraw_page(self):self.transaction_form("Withdraw Money","Withdrawal")

    def transfer_page(self):
        p=self.page_title("Transfer Money","Move funds between bank accounts")
        card=self.card(p,padx=30,pady=24);card.pack(fill="x")
        mine=self.accounts.get_accounts_by_customer_id(self.customer.id,include_closed=False);nums=[a.account_number for a in mine]
        allacc=[a for a in self.accounts.get_all_accounts() if a.status==ACCOUNT_STATUS_ACTIVE]
        dest=[a.account_number for a in allacc]
        src=tk.StringVar(value=nums[0] if nums else "");dst=tk.StringVar();amt=tk.StringVar();desc=tk.StringVar()
        for lab,var,vals in (("From Account",src,nums),("To Account",dst,dest),("Amount (Rs.)",amt,None),("Description",desc,None)):
            tk.Label(card,text=lab,bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(3,3))
            if vals is not None:ttk.Combobox(card,textvariable=var,values=vals,state="readonly").pack(fill="x",pady=(0,12))
            else:ttk.Entry(card,textvariable=var).pack(fill="x",pady=(0,12))
        status=self.inline_status(card);status.pack(fill="x",pady=(0,6))
        def submit():
            try:a=Decimal(amt.get()).quantize(Decimal("0.01"))
            except InvalidOperation:self.set_status(status,"Enter a valid amount.");return
            ok,msg=self.transactions.transfer(src.get(),dst.get(),a,desc.get() or "Customer transfer")
            if ok:self.toast(msg,"success");self.customer_overview()
            else:self.set_status(status,msg)
        self.button(card,"SEND TRANSFER",submit,"accent").pack(anchor="w")

    def customer_transactions(self):
        p=self.page_title("Transaction History","Your complete account activity")
        accounts=self.accounts.get_accounts_by_customer_id(self.customer.id,include_closed=True);ids=[a.id for a in accounts]
        tree=self.make_tree(p,[("txn","Transaction ID"),("acc","Account"),("type","Type"),("amount","Amount"),("before","Before"),("after","After"),("desc","Description"),("date","Date"),("status","Status")],[175,120,135,120,120,120,230,150,100],14)
        if ids:
            conn=self.db.get_connection();q=','.join('?'*len(ids));rows=conn.execute(f"SELECT t.transaction_id,a.account_number,t.transaction_type,t.amount,t.balance_before,t.balance_after,t.description,t.transaction_date,t.status FROM transactions t JOIN accounts a ON a.id=t.account_id WHERE t.account_id IN ({q}) ORDER BY t.id DESC",ids).fetchall();conn.close()
            for r in rows:tree.insert("","end",values=(r[0],r[1],r[2],f"Rs. {Decimal(str(r[3])):,.2f}",f"Rs. {Decimal(str(r[4])):,.2f}",f"Rs. {Decimal(str(r[5])):,.2f}",r[6] or "",r[7],r[8]))

    def customer_profile(self):
        p=self.page_title("Profile & Security","Update your contact details or change your password")
        card=self.card(p,padx=25,pady=22);card.pack(fill="x",pady=(0,18))
        vars={k:tk.StringVar(value=getattr(self.customer,k,"")) for k in ("full_name","phone","email","address")}
        for lab,key in (("Full Name","full_name"),("Phone","phone"),("Email","email"),("Address","address")):
            tk.Label(card,text=lab,bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(4,3));ttk.Entry(card,textvariable=vars[key]).pack(fill="x",pady=(0,9))
        profile_status=self.inline_status(card);profile_status.pack(fill="x",pady=(0,4))
        def save():
            ok,msg=self.customers.update_customer_profile(self.customer.id,vars['full_name'].get(),vars['phone'].get(),vars['email'].get(),vars['address'].get())
            if ok:self.customer=self.customers.get_customer_by_id(self.customer.id);self.toast(msg,"success");self.show_customer()
            else:self.set_status(profile_status,msg)
        self.button(card,"UPDATE PROFILE",save,"accent").pack(anchor="w",pady=8)
        sec=self.card(p,padx=25,pady=22);sec.pack(fill="x")
        tk.Label(sec,text="Change password",bg=WHITE,fg=TEXT,font=("Segoe UI",14,"bold")).pack(anchor="w",pady=(0,12))
        old=tk.StringVar();new=tk.StringVar();confirm=tk.StringVar()
        for lab,var in (("Current password",old),("New password",new),("Confirm new password",confirm)):
            tk.Label(sec,text=lab,bg=WHITE,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(4,3));ttk.Entry(sec,textvariable=var,show="•").pack(fill="x",pady=(0,8))
        pw_status=self.inline_status(sec);pw_status.pack(fill="x",pady=(0,4))
        def change():
            if new.get()!=confirm.get():self.set_status(pw_status,"New passwords do not match.");return
            ok,msg=self.auth.change_customer_password(self.customer.id,old.get(),new.get())
            if ok:old.set("");new.set("");confirm.set("");self.toast(msg,"success")
            else:self.set_status(pw_status,msg)
        self.button(sec,"CHANGE PASSWORD",change).pack(anchor="w",pady=8)


def run_gui():
    app=BankGUI()
    app.mainloop()
