"""
Car Rental Management System - Configuration
Customized and branded for Maryam Fahim.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = str(BASE_DIR / "car_rental.db")
LOG_FILE_PATH = str(BASE_DIR / "car_rental.log")
REPORTS_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# Brand / Owner
# ------------------------------------------------------------
OWNER_NAME = "Maryam Fahim"
BRAND_NAME = "Maryam Fahim"
APP_TITLE = "Maryam Fahim • Car Rental"
APP_SUBTITLE = "Smart Fleet Management • Rentals • Payments • Analytics"
APP_VERSION = "2.0.0"
COPYRIGHT_YEAR = "2026"
# Financial & Rental Defaults
DEFAULT_SECURITY_DEPOSIT = 5000.0
DEFAULT_CURRENCY = "PKR"

CAR_CATEGORIES = [
    "Economy", "Sedan", "SUV", "Luxury", "Sports", "Van", "Hatchback"
]

CAR_STATUSES = ["Available", "Rented", "Maintenance"]
RENTAL_STATUSES = ["Active", "Completed", "Cancelled"]
PAYMENT_METHODS = ["Cash", "Card", "Bank Transfer"]
PAYMENT_STATUSES = ["Paid", "Pending", "Refunded"]

# ------------------------------------------------------------
# Premium dark/light UI system
# ------------------------------------------------------------
THEME = {
    "bg_dark": "#0B1220",
    "sidebar_bg": "#111827",
    "sidebar_hover": "#1F2937",
    "sidebar_active": "#4F46E5",
    "sidebar_text": "#F9FAFB",
    "sidebar_muted": "#9CA3AF",

    "main_bg": "#F5F7FB",
    "card_bg": "#FFFFFF",
    "card_border": "#E5E7EB",

    "text_primary": "#111827",
    "text_secondary": "#4B5563",
    "text_muted": "#9CA3AF",

    "primary": "#4F46E5",
    "primary_hover": "#4338CA",
    "primary_light": "#EEF2FF",

    "success": "#059669",
    "success_hover": "#047857",
    "success_light": "#D1FAE5",

    "warning": "#D97706",
    "warning_hover": "#B45309",
    "warning_light": "#FEF3C7",

    "danger": "#DC2626",
    "danger_hover": "#B91C1C",
    "danger_light": "#FEE2E2",

    "purple": "#7C3AED",
    "purple_light": "#EDE9FE",

    "cyan": "#0891B2",
    "cyan_light": "#CFFAFE",

    "table_header_bg": "#111827",
    "table_header_fg": "#FFFFFF",
    "table_row_alt": "#F8FAFC",
    "table_row_select": "#E0E7FF",
}

FONTS = {
    "brand": ("Segoe UI", 19, "bold"),
    "hero": ("Segoe UI", 28, "bold"),
    "title_large": ("Segoe UI", 20, "bold"),
    "title_medium": ("Segoe UI", 15, "bold"),
    "title_small": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10, "normal"),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9, "normal"),
    "small_bold": ("Segoe UI", 9, "bold"),
    "monospace": ("Consolas", 10, "normal"),
    "receipt_header": ("Courier New", 12, "bold"),
    "receipt_body": ("Courier New", 10, "normal"),
}
