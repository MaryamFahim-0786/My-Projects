"""
Welcome & Authentication View
Provides a clean, modern gateway for Admin Login, Customer Login, and Customer Registration.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from config import APP_TITLE, APP_SUBTITLE, APP_VERSION, OWNER_NAME, THEME, FONTS, ASSETS_DIR
from models.admin import Admin
from models.customer import Customer
from utils.validators import (
    validate_name, validate_cnic, validate_phone,
    validate_email, validate_username, validate_password
)
from views.styles import center_window, create_button

class WelcomeView(tk.Frame):
    """Modern hero landing screen with seamless tabbed login and registration forms."""

    def __init__(
        self,
        parent,
        on_admin_login_success: Callable[[Admin], None],
        on_customer_login_success: Callable[[Customer], None],
        on_exit: Callable[[], None]
    ):
        super().__init__(parent, bg=THEME["main_bg"])
        self.parent = parent
        self.on_admin_login_success = on_admin_login_success
        self.on_customer_login_success = on_customer_login_success
        self.on_exit = on_exit

        self._build_ui()

    def _build_ui(self):
        # Top Header Banner
        banner = tk.Frame(self, bg=THEME["sidebar_bg"], pady=28, padx=40)
        banner.pack(fill="x")

        # App Brand Title
        title_lbl = tk.Label(
            banner,
            text=f"✦ {OWNER_NAME.upper()}",
            font=FONTS["hero"],
            fg=THEME["sidebar_text"],
            bg=THEME["sidebar_bg"]
        )
        title_lbl.pack()

        subtitle_lbl = tk.Label(
            banner,
            text=f"{APP_SUBTITLE}  •  v{APP_VERSION}",
            font=FONTS["body"],
            fg=THEME["sidebar_muted"],
            bg=THEME["sidebar_bg"]
        )
        subtitle_lbl.pack(pady=(4, 0))

        # Main Container: split into a showroom visual panel (left) and the login card (right)
        main_container = tk.Frame(self, bg=THEME["main_bg"], pady=22)
        main_container.pack(fill="both", expand=True)

        showroom_panel = tk.Frame(main_container, bg=THEME["sidebar_bg"], width=380)
        showroom_panel.pack(side="left", fill="y", padx=(24, 0), pady=4)
        showroom_panel.pack_propagate(False)
        self._build_showroom_panel(showroom_panel)

        right_panel = tk.Frame(main_container, bg=THEME["main_bg"])
        right_panel.pack(side="right", fill="both", expand=True)

        # Card Frame
        card = tk.Frame(
            right_panel,
            bg=THEME["card_bg"],
            highlightbackground=THEME["card_border"],
            highlightthickness=1,
            padx=30,
            pady=20,
            width=560
        )
        card.pack(expand=True)

        # Tab Navigation Header
        identity = tk.Frame(card, bg=THEME["primary_light"], padx=14, pady=10)
        identity.pack(fill="x", pady=(0, 14))
        tk.Label(identity, text="MARYAM FAHIM", font=FONTS["small_bold"],
                 fg=THEME["primary"], bg=THEME["primary_light"]).pack(anchor="w")
        tk.Label(identity, text="Your personal fleet & rental workspace",
                 font=FONTS["small"], fg=THEME["text_secondary"],
                 bg=THEME["primary_light"]).pack(anchor="w", pady=(2, 0))

        tab_header = tk.Frame(card, bg=THEME["card_bg"])
        tab_header.pack(fill="x", pady=(0, 20))

        self.btn_tab_cust_login = tk.Button(
            tab_header,
            text="Customer Login",
            font=FONTS["body_bold"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda: self._switch_tab("cust_login")
        )
        self.btn_tab_cust_login.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_tab_admin_login = tk.Button(
            tab_header,
            text="Admin Login",
            font=FONTS["body_bold"],
            bg=THEME["main_bg"],
            fg=THEME["text_secondary"],
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda: self._switch_tab("admin_login")
        )
        self.btn_tab_admin_login.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_tab_cust_reg = tk.Button(
            tab_header,
            text="New Registration",
            font=FONTS["body_bold"],
            bg=THEME["main_bg"],
            fg=THEME["text_secondary"],
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda: self._switch_tab("cust_reg")
        )
        self.btn_tab_cust_reg.pack(side="left", expand=True, fill="x", padx=2)

        # Content Area for Forms
        self.form_area = tk.Frame(card, bg=THEME["card_bg"])
        self.form_area.pack(fill="both", expand=True)

        # Build individual form frames
        self._build_customer_login_form()
        self._build_admin_login_form()
        self._build_customer_reg_form()

        # Exit & Info Row
        footer_frame = tk.Frame(self, bg=THEME["main_bg"], pady=10)
        footer_frame.pack(fill="x", side="bottom")

        create_button(
            footer_frame,
            text=" Exit Application",
            command=self.on_exit,
            bg_color=THEME["danger"],
            hover_color=THEME["danger_hover"],
            font=FONTS["small_bold"]
        ).pack(side="right", padx=30)

        # Start with Customer Login tab
        self._switch_tab("cust_login")

    def _build_showroom_panel(self, panel: tk.Frame):
        """Renders the automotive showroom visual with a branded overlay tagline."""
        showroom_path = ASSETS_DIR / "showroom.png"
        self._showroom_img = None

        if showroom_path.exists():
            try:
                raw = tk.PhotoImage(file=str(showroom_path))
                # Downscale to a sensible banner size using integer subsampling.
                factor = max(1, raw.width() // 380)
                self._showroom_img = raw.subsample(factor, factor) if factor > 1 else raw
            except tk.TclError:
                self._showroom_img = None

        if self._showroom_img is not None:
            tk.Label(panel, image=self._showroom_img, bg=THEME["sidebar_bg"]).pack(fill="x")
        else:
            # Graceful fallback if the asset is missing or unreadable.
            tk.Frame(panel, bg=THEME["sidebar_bg"], height=220).pack(fill="x")

        overlay = tk.Frame(panel, bg=THEME["sidebar_bg"], padx=20, pady=18)
        overlay.pack(fill="both", expand=True)

        tk.Label(
            overlay,
            text="Drive Your Way",
            font=FONTS["title_large"],
            fg=THEME["sidebar_text"],
            bg=THEME["sidebar_bg"]
        ).pack(anchor="w", pady=(4, 2))

        tk.Label(
            overlay,
            text="Premium vehicles, transparent pricing, and a\nrental experience built around you.",
            font=FONTS["small"],
            fg=THEME["sidebar_muted"],
            bg=THEME["sidebar_bg"],
            justify="left"
        ).pack(anchor="w")

        for line in ("✓ Verified fleet condition", "✓ Instant digital receipts", "✓ Transparent PKR pricing"):
            tk.Label(
                overlay,
                text=line,
                font=FONTS["small_bold"],
                fg=THEME["primary_light"],
                bg=THEME["sidebar_bg"]
            ).pack(anchor="w", pady=(10, 0))

    def _switch_tab(self, tab_key: str):
        """Switches active form view and updates tab button styles."""
        tabs = {
            "cust_login": (self.cust_login_frame, self.btn_tab_cust_login),
            "admin_login": (self.admin_login_frame, self.btn_tab_admin_login),
            "cust_reg": (self.cust_reg_frame, self.btn_tab_cust_reg),
        }

        for key, (frame, btn) in tabs.items():
            if key == tab_key:
                frame.pack(fill="both", expand=True)
                btn.config(bg=THEME["primary"], fg="#FFFFFF")
            else:
                frame.pack_forget()
                btn.config(bg=THEME["main_bg"], fg=THEME["text_secondary"])

    # ------------------ Customer Login Form ------------------
    def _build_customer_login_form(self):
        self.cust_login_frame = tk.Frame(self.form_area, bg=THEME["card_bg"])

        tk.Label(
            self.cust_login_frame,
            text="Welcome Back!",
            font=FONTS["title_medium"],
            fg=THEME["text_primary"],
            bg=THEME["card_bg"]
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self.cust_login_frame,
            text="Please enter your customer credentials to access vehicle rental portal.",
            font=FONTS["small"],
            fg=THEME["text_secondary"],
            bg=THEME["card_bg"]
        ).pack(anchor="w", pady=(0, 16))

        # Username
        tk.Label(self.cust_login_frame, text="Username", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).pack(anchor="w")
        self.cust_user_ent = ttk.Entry(self.cust_login_frame, font=FONTS["body"])
        self.cust_user_ent.pack(fill="x", pady=(2, 12))
        self.cust_user_ent.insert(0, "Fahim") # demo default

        # Password
        tk.Label(self.cust_login_frame, text="Password", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).pack(anchor="w")
        self.cust_pass_ent = ttk.Entry(self.cust_login_frame, font=FONTS["body"], show="●")
        self.cust_pass_ent.pack(fill="x", pady=(2, 18))
        self.cust_pass_ent.insert(0, "customer123") # demo default

        # Buttons
        btn_box = tk.Frame(self.cust_login_frame, bg=THEME["card_bg"])
        btn_box.pack(fill="x", pady=(6, 10))

        create_button(
            btn_box,
            text="Login to Portal",
            command=self._handle_customer_login,
            bg_color=THEME["primary"],
            hover_color=THEME["primary_hover"]
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        create_button(
            btn_box,
            text="Clear",
            command=lambda: (self.cust_user_ent.delete(0, tk.END), self.cust_pass_ent.delete(0, tk.END)),
            bg_color=THEME["sidebar_hover"],
            hover_color=THEME["sidebar_bg"]
        ).pack(side="right", padx=(4, 0))

        # Quick Switch link
        link_lbl = tk.Label(
            self.cust_login_frame,
            text="Don't have an account? Click 'New Registration' above.",
            font=FONTS["small"],
            fg=THEME["primary"],
            bg=THEME["card_bg"],
            cursor="hand2"
        )
        link_lbl.pack(pady=(10, 0))
        link_lbl.bind("<Button-1>", lambda e: self._switch_tab("cust_reg"))

        tk.Label(
            self.cust_login_frame,
            text="Demo credentials: Fahim / customer123",
            font=FONTS["small"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"]
        ).pack(pady=(4, 0))

    def _handle_customer_login(self):
        user = self.cust_user_ent.get().strip()
        pwd = self.cust_pass_ent.get().strip()

        if not user or not pwd:
            messagebox.showwarning("Missing Credentials", "Please enter both Username and Password.")
            return

        customer = Customer.authenticate(user, pwd)
        if customer:
            self.on_customer_login_success(customer)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")

    # ------------------ Admin Login Form ------------------
    def _build_admin_login_form(self):
        self.admin_login_frame = tk.Frame(self.form_area, bg=THEME["card_bg"])

        tk.Label(
            self.admin_login_frame,
            text="Administrator Sign In",
            font=FONTS["title_medium"],
            fg=THEME["text_primary"],
            bg=THEME["card_bg"]
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self.admin_login_frame,
            text="Access administrative controls, fleet management, and financial reports.",
            font=FONTS["small"],
            fg=THEME["text_secondary"],
            bg=THEME["card_bg"]
        ).pack(anchor="w", pady=(0, 16))

        # Username
        tk.Label(self.admin_login_frame, text="Admin Username", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).pack(anchor="w")
        self.admin_user_ent = ttk.Entry(self.admin_login_frame, font=FONTS["body"])
        self.admin_user_ent.pack(fill="x", pady=(2, 12))
        self.admin_user_ent.insert(0, "maryam") # demo default

        # Password
        tk.Label(self.admin_login_frame, text="Admin Password", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).pack(anchor="w")
        self.admin_pass_ent = ttk.Entry(self.admin_login_frame, font=FONTS["body"], show="●")
        self.admin_pass_ent.pack(fill="x", pady=(2, 18))
        self.admin_pass_ent.insert(0, "admin123") # demo default

        # Buttons
        btn_box = tk.Frame(self.admin_login_frame, bg=THEME["card_bg"])
        btn_box.pack(fill="x", pady=(6, 10))

        create_button(
            btn_box,
            text="Admin Secure Login",
            command=self._handle_admin_login,
            bg_color=THEME["sidebar_bg"],
            hover_color=THEME["sidebar_hover"]
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        create_button(
            btn_box,
            text="Clear",
            command=lambda: (self.admin_user_ent.delete(0, tk.END), self.admin_pass_ent.delete(0, tk.END)),
            bg_color=THEME["card_border"],
            fg_color=THEME["text_primary"],
            hover_color=THEME["main_bg"]
        ).pack(side="right", padx=(4, 0))

        tk.Label(
            self.admin_login_frame,
            text="Demo credentials: maryam / admin123",
            font=FONTS["small"],
            fg=THEME["text_muted"],
            bg=THEME["card_bg"]
        ).pack(pady=(10, 0))

    def _handle_admin_login(self):
        user = self.admin_user_ent.get().strip()
        pwd = self.admin_pass_ent.get().strip()

        if not user or not pwd:
            messagebox.showwarning("Missing Credentials", "Please enter both Admin Username and Password.")
            return

        admin = Admin.authenticate(user, pwd)
        if admin:
            self.on_admin_login_success(admin)
        else:
            messagebox.showerror("Login Failed", "Invalid admin credentials. (Default demo: maryam / admin123)")

    # ------------------ Customer Registration Form ------------------
    def _build_customer_reg_form(self):
        self.cust_reg_frame = tk.Frame(self.form_area, bg=THEME["card_bg"])

        tk.Label(
            self.cust_reg_frame,
            text="Create Customer Account",
            font=FONTS["title_medium"],
            fg=THEME["text_primary"],
            bg=THEME["card_bg"]
        ).pack(anchor="w", pady=(0, 4))

        # Two-column layout for registration fields
        grid_frame = tk.Frame(self.cust_reg_frame, bg=THEME["card_bg"])
        grid_frame.pack(fill="both", expand=True, pady=(10, 10))

        # Full Name
        tk.Label(grid_frame, text="Full Name *", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.reg_name = ttk.Entry(grid_frame, font=FONTS["body"])
        self.reg_name.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))

        # CNIC
        tk.Label(grid_frame, text="CNIC (XXXXX-XXXXXXX-X) *", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.reg_cnic = ttk.Entry(grid_frame, font=FONTS["body"])
        self.reg_cnic.grid(row=1, column=1, sticky="ew", padx=4, pady=(0, 8))

        # Phone
        tk.Label(grid_frame, text="Phone Number (03XX-XXXXXXX) *", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.reg_phone = ttk.Entry(grid_frame, font=FONTS["body"])
        self.reg_phone.grid(row=3, column=0, sticky="ew", padx=4, pady=(0, 8))

        # Email
        tk.Label(grid_frame, text="Email Address *", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).grid(row=2, column=1, sticky="w", padx=4, pady=2)
        self.reg_email = ttk.Entry(grid_frame, font=FONTS["body"])
        self.reg_email.grid(row=3, column=1, sticky="ew", padx=4, pady=(0, 8))

        # Address
        tk.Label(grid_frame, text="Full Address", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).grid(row=4, column=0, columnspan=2, sticky="w", padx=4, pady=2)
        self.reg_address = ttk.Entry(grid_frame, font=FONTS["body"])
        self.reg_address.grid(row=5, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 8))

        # Username
        tk.Label(grid_frame, text="Choose Username *", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).grid(row=6, column=0, sticky="w", padx=4, pady=2)
        self.reg_username = ttk.Entry(grid_frame, font=FONTS["body"])
        self.reg_username.grid(row=7, column=0, sticky="ew", padx=4, pady=(0, 8))

        # Password
        tk.Label(grid_frame, text="Password (Min 6 chars) *", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).grid(row=8, column=0, sticky="w", padx=4, pady=2)
        self.reg_password = ttk.Entry(grid_frame, font=FONTS["body"], show="●")
        self.reg_password.grid(row=9, column=0, sticky="ew", padx=4, pady=(0, 8))

        # Confirm Password
        tk.Label(grid_frame, text="Confirm Password *", font=FONTS["small_bold"], fg=THEME["text_primary"], bg=THEME["card_bg"]).grid(row=8, column=1, sticky="w", padx=4, pady=2)
        self.reg_confirm_password = ttk.Entry(grid_frame, font=FONTS["body"], show="●")
        self.reg_confirm_password.grid(row=9, column=1, sticky="ew", padx=4, pady=(0, 8))

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)

        # Register Action Buttons
        btn_box = tk.Frame(self.cust_reg_frame, bg=THEME["card_bg"])
        btn_box.pack(fill="x", pady=(10, 0))

        create_button(
            btn_box,
            text="Submit Registration",
            command=self._handle_customer_registration,
            bg_color=THEME["success"],
            hover_color=THEME["success_hover"]
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        create_button(
            btn_box,
            text="Clear Form",
            command=self._clear_reg_form,
            bg_color=THEME["card_border"],
            fg_color=THEME["text_primary"],
            hover_color=THEME["main_bg"]
        ).pack(side="right", padx=(4, 0))

    def _clear_reg_form(self):
        for ent in [self.reg_name, self.reg_cnic, self.reg_phone, self.reg_email, self.reg_address, self.reg_username, self.reg_password, self.reg_confirm_password]:
            ent.delete(0, tk.END)

    def _handle_customer_registration(self):
        name = self.reg_name.get().strip()
        cnic = self.reg_cnic.get().strip()
        phone = self.reg_phone.get().strip()
        email = self.reg_email.get().strip()
        address = self.reg_address.get().strip()
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm_pw = self.reg_confirm_password.get()

        # Validations
        valid, msg = validate_name(name)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return

        valid, msg = validate_cnic(cnic)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return

        valid, msg = validate_phone(phone)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return

        valid, msg = validate_email(email)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return

        valid, msg = validate_username(username)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return

        valid, msg = validate_password(password, confirm_pw)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return

        # Attempt registration
        success, res_msg, cust_id = Customer.register(
            full_name=name,
            cnic=cnic,
            phone=phone,
            email=email,
            address=address,
            username=username,
            password_plain=password
        )

        if success:
            messagebox.showinfo("Registration Successful", res_msg)
            self._clear_reg_form()
            # Switch to login tab and prefill username
            self._switch_tab("cust_login")
            self.cust_user_ent.delete(0, tk.END)
            self.cust_user_ent.insert(0, username)
            self.cust_pass_ent.delete(0, tk.END)
        else:
            messagebox.showerror("Registration Error", res_msg)
