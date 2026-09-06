"""
Helper Utilities
Provides formatting, date conversions, logging configuration, CSV exporting, and receipt generation.
"""

import csv
import logging
import os
import subprocess
import sys
from datetime import datetime, date
from pathlib import Path
from typing import List, Any, Optional

from config import OWNER_NAME, LOG_FILE_PATH, REPORTS_DIR, DEFAULT_CURRENCY

# Global Logger Instance
logger = logging.getLogger("CarRentalSystem")

def setup_logger():
    """Configures application-wide logging to file and console."""
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Stream handler (console)
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

def format_currency(amount: Any, short: bool = False) -> str:
    """Formats numeric amount to standard currency string (e.g. PKR 15,000.00).

    When short=True, large values are abbreviated (e.g. PKR 1.2K, PKR 3.4M) —
    useful for compact chart labels.
    """
    try:
        val = float(amount or 0.0)
    except (ValueError, TypeError):
        val = 0.0

    if short:
        abs_val = abs(val)
        if abs_val >= 1_000_000:
            return f"{DEFAULT_CURRENCY} {val / 1_000_000:,.1f}M"
        if abs_val >= 1_000:
            return f"{DEFAULT_CURRENCY} {val / 1_000:,.1f}K"
        return f"{DEFAULT_CURRENCY} {val:,.0f}"

    return f"{DEFAULT_CURRENCY} {val:,.2f}"

def format_date_display(date_val: Any) -> str:
    """
    Converts ISO date string (YYYY-MM-DD) or datetime/date object to user-friendly format (e.g. 27-Aug-2026).
    """
    if not date_val:
        return "N/A"
    
    if isinstance(date_val, (datetime, date)):
        return date_val.strftime("%d-%b-%Y")
    
    date_str = str(date_val).strip()
    # Try YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d-%b-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime("%d-%b-%Y")
        except ValueError:
            continue
    return date_str

def today_iso() -> str:
    """Returns today's date in YYYY-MM-DD format."""
    return date.today().strftime("%Y-%m-%d")

def export_to_csv(filename_prefix: str, headers: List[str], data_rows: List[List[Any]]) -> str:
    """
    Exports provided headers and row data into a CSV file in the reports/ directory.
    Returns the absolute path to the generated CSV file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_prefix = filename_prefix.replace(".csv", "").replace(" ", "_").lower()
    filename = f"{clean_prefix}_{timestamp}.csv"
    file_path = REPORTS_DIR / filename
    
    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in data_rows:
            writer.writerow(row)
            
    logger.info(f"Report exported successfully to {file_path}")
    return str(file_path)

def open_file_externally(file_path: Any) -> bool:
    """Opens a file with the operating system's default application.

    Uses os.startfile on Windows, 'open' on macOS, and 'xdg-open' on Linux.
    Returns True if the open command was launched successfully, False otherwise
    (e.g. no CSV viewer is associated with .csv files, or the file is missing).
    """
    path_str = str(file_path)
    try:
        if sys.platform.startswith("win"):
            os.startfile(path_str)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path_str])
        else:
            subprocess.Popen(["xdg-open", path_str])
        logger.info(f"Opened file externally: {path_str}")
        return True
    except Exception as e:
        logger.error(f"Could not auto-open file '{path_str}': {e}")
        return False

def generate_receipt_text(
    rental_id: Any,
    customer_name: str,
    customer_cnic: str,
    customer_phone: str,
    car_number: str,
    car_brand: str,
    car_model: str,
    rental_date: str,
    expected_return_date: str,
    rental_days: int,
    daily_rate: float,
    rental_amount: float,
    security_deposit: float,
    total_amount: float,
    payment_method: str = "Cash",
    payment_status: str = "Paid",
    actual_return_date: Optional[str] = None,
    late_days: int = 0,
    late_charges: float = 0.0,
    final_amount: Optional[float] = None
) -> str:
    """
    Generates a structured, printable ASCII invoice/receipt.
    """
    width = 58
    border = "=" * width
    divider = "-" * width
    
    disp_rental_date = format_date_display(rental_date)
    disp_return_date = format_date_display(expected_return_date)
    
    receipt_lines = [
        border,
        f"{OWNER_NAME.upper() + ' CAR RENTAL':^{width}}",
        f"{'OFFICIAL RENTAL INVOICE & RECEIPT':^{width}}",
        border,
        f" Receipt Generated : {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}",
        f" Rental Invoice ID : #{rental_id}",
        divider,
        " CUSTOMER INFORMATION:",
        f"  Name            : {customer_name}",
        f"  CNIC / ID       : {customer_cnic}",
        f"  Contact Phone   : {customer_phone}",
        divider,
        " VEHICLE DETAILS:",
        f"  Registration No : {car_number}",
        f"  Make & Model    : {car_brand} {car_model}",
        f"  Daily Rate      : {format_currency(daily_rate)} / day",
        divider,
        " RENTAL DURATION & SCHEDULE:",
        f"  Start Date      : {disp_rental_date}",
        f"  Return Due Date : {disp_return_date}",
        f"  Total Duration  : {rental_days} day(s)",
        divider,
        " FINANCIAL BREAKDOWN:",
        f"  Rental Charge ({rental_days}d x {format_currency(daily_rate).replace('PKR ', '')}) : {format_currency(rental_amount):>18}",
        f"  Refundable Security Deposit  : {format_currency(security_deposit):>18}",
        divider,
        f"  INITIAL TOTAL PAYABLE        : {format_currency(total_amount):>18}",
    ]
    
    if actual_return_date:
        receipt_lines.extend([
            divider,
            " RETURN & LATE SETTLEMENT:",
            f"  Actual Return Date : {format_date_display(actual_return_date)}",
            f"  Overdue Days       : {late_days} day(s)",
            f"  Late Penalty Fee   : {format_currency(late_charges):>18}",
            divider,
            f"  FINAL ADJUSTED TOTAL         : {format_currency(final_amount if final_amount is not None else total_amount + late_charges):>18}"
        ])

    receipt_lines.extend([
        divider,
        f" Payment Method : {payment_method.upper()}",
        f" Payment Status : {payment_status.upper()}",
        border,
        f"{'Thank you for choosing our Car Rental Service!':^{width}}",
        f"{'Drive Safely & Follow Traffic Regulations':^{width}}",
        border
    ])
    
    return "\n".join(receipt_lines)
