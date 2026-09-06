"""
Premium UI Styling & Reusable Components
Branded for Maryam Fahim.
"""

import tkinter as tk
from tkinter import ttk
from typing import Tuple, List, Dict, Any, Optional

from config import THEME, FONTS, OWNER_NAME


def apply_custom_styles(root: tk.Tk):
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(
        "Custom.Treeview",
        background=THEME["card_bg"],
        foreground=THEME["text_primary"],
        fieldbackground=THEME["card_bg"],
        font=FONTS["body"],
        rowheight=34,
        borderwidth=0,
        relief="flat",
        padding=(4, 0),
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=THEME["table_header_bg"],
        foreground=THEME["table_header_fg"],
        font=FONTS["small_bold"],
        relief="flat",
        padding=(10, 9),
    )
    style.map(
        "Custom.Treeview.Heading",
        background=[("active", THEME["sidebar_active"])],
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", THEME["table_row_select"])],
        foreground=[("selected", THEME["text_primary"])],
    )

    style.configure(
        "TCombobox",
        fieldbackground=THEME["card_bg"],
        background=THEME["card_bg"],
        foreground=THEME["text_primary"],
        font=FONTS["body"],
        padding=7,
        borderwidth=0,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", THEME["card_bg"])],
        foreground=[("readonly", THEME["text_primary"])],
    )

    style.configure(
        "TEntry",
        fieldbackground=THEME["card_bg"],
        foreground=THEME["text_primary"],
        padding=8,
        borderwidth=1,
    )

    style.configure(
        "Vertical.TScrollbar",
        background=THEME["main_bg"],
        troughcolor=THEME["card_bg"],
        borderwidth=0,
        arrowsize=13,
    )


def center_window(window: tk.Tk or tk.Toplevel, width: int, height: int):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = max(0, (screen_width - width) // 2)
    y = max(0, (screen_height - height) // 2 - 30)
    window.geometry(f"{width}x{height}+{x}+{y}")


def make_card(parent, **kwargs):
    defaults = dict(
        bg=THEME["card_bg"],
        highlightbackground=THEME["card_border"],
        highlightthickness=1,
        bd=0,
    )
    defaults.update(kwargs)
    return tk.Frame(parent, **defaults)


def create_button(
    parent,
    text: str,
    command,
    bg_color: str = THEME["primary"],
    fg_color: str = "#FFFFFF",
    hover_color: Optional[str] = None,
    font=FONTS["body_bold"],
    padx: int = 14,
    pady: int = 8,
    width: Optional[int] = None,
) -> tk.Button:
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_color,
        fg=fg_color,
        activebackground=hover_color or bg_color,
        activeforeground=fg_color,
        font=font,
        bd=0,
        padx=padx,
        pady=pady,
        relief="flat",
        cursor="hand2",
        highlightthickness=0,
    )
    if width:
        btn.config(width=width)

    def on_enter(_):
        if hover_color:
            btn.config(bg=hover_color)

    def on_leave(_):
        btn.config(bg=bg_color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


class StatCard(tk.Frame):
    """Premium KPI card with accent rail, icon badge, metric and optional helper text."""

    def __init__(
        self,
        parent,
        title: str,
        value: str,
        subtext: str = "",
        accent_color: str = THEME["primary"],
        icon_text: str = "●",
        **kwargs
    ):
        super().__init__(
            parent,
            bg=THEME["card_bg"],
            highlightbackground=THEME["card_border"],
            highlightthickness=1,
            bd=0,
            **kwargs
        )

        rail = tk.Frame(self, bg=accent_color, width=4)
        rail.pack(side="left", fill="y")

        content = tk.Frame(self, bg=THEME["card_bg"], padx=15, pady=14)
        content.pack(fill="both", expand=True)

        row = tk.Frame(content, bg=THEME["card_bg"])
        row.pack(fill="x")

        tk.Label(
            row, text=title.upper(), font=FONTS["small_bold"],
            fg=THEME["text_muted"], bg=THEME["card_bg"]
        ).pack(side="left")

        icon = tk.Label(
            row, text=icon_text, font=("Segoe UI", 13, "bold"),
            fg=accent_color, bg=THEME["card_bg"]
        )
        icon.pack(side="right")

        self.val_lbl = tk.Label(
            content, text=value, font=FONTS["title_large"],
            fg=THEME["text_primary"], bg=THEME["card_bg"]
        )
        self.val_lbl.pack(anchor="w", pady=(7, 1))

        if subtext:
            self.sub_lbl = tk.Label(
                content, text=subtext, font=FONTS["small"],
                fg=THEME["text_secondary"], bg=THEME["card_bg"]
            )
            self.sub_lbl.pack(anchor="w")

    def update_value(self, new_value: str, new_subtext: Optional[str] = None):
        self.val_lbl.config(text=new_value)
        if new_subtext is not None and hasattr(self, "sub_lbl"):
            self.sub_lbl.config(text=new_subtext)


STATUS_COLORS: Dict[str, str] = {
    "Available": THEME["success"],
    "Paid": THEME["success"],
    "Completed": THEME["success"],
    "Active": THEME["primary"],
    "Rented": THEME["purple"],
    "Pending": THEME["warning"],
    "Maintenance": THEME["warning"],
    "Cancelled": THEME["danger"],
    "Failed": THEME["danger"],
    "Refunded": THEME["cyan"],
}


def configure_status_tags(tree: ttk.Treeview):
    """Registers colored foreground tags (by status label) on a Treeview.

    Row-striping tags (evenrow/oddrow) set the background; status tags only
    set the foreground/font, so combining tags=(row_tag, status_label) keeps
    the striped background while coloring the status text.
    """
    for status, color in STATUS_COLORS.items():
        tree.tag_configure(status, foreground=color, font=FONTS["small_bold"])


def draw_bar_chart(
    parent,
    data: List[Tuple[str, float, str]],
    width: int = 380,
    height: int = 170,
    value_formatter: Optional[Any] = None,
) -> tk.Canvas:
    """Renders a compact vertical bar chart on a plain tk.Canvas (no third-party deps).

    data: list of (label, value, bar_color) tuples.
    value_formatter: optional callable(value) -> str for the value shown above each bar.
    """
    canvas = tk.Canvas(parent, width=width, height=height, bg=THEME["card_bg"], highlightthickness=0)
    canvas.pack(fill="x")

    if not data:
        canvas.create_text(
            width // 2, height // 2, text="No data available yet.",
            fill=THEME["text_muted"], font=FONTS["small"]
        )
        return canvas

    values = [max(0.0, float(v)) for _, v, _ in data]
    max_val = max(values) if max(values) > 0 else 1.0

    top_pad, bottom_pad = 26, 28
    plot_h = height - top_pad - bottom_pad
    n = len(data)
    slot_w = width / n
    bar_w = min(52, slot_w * 0.5)

    fmt = value_formatter or (lambda v: f"{v:,.0f}")

    for i, (label, value, color) in enumerate(data):
        value = max(0.0, float(value))
        bar_h = (value / max_val) * plot_h if max_val > 0 else 0
        x_center = slot_w * i + slot_w / 2
        x0 = x_center - bar_w / 2
        x1 = x_center + bar_w / 2
        y1 = top_pad + plot_h
        y0 = y1 - bar_h

        canvas.create_text(x_center, top_pad - 12, text=fmt(value), fill=THEME["text_primary"], font=FONTS["small_bold"])
        if bar_h > 0:
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
        else:
            canvas.create_line(x0, y1, x1, y1, fill=THEME["card_border"], width=2)
        canvas.create_text(x_center, y1 + 14, text=label, fill=THEME["text_secondary"], font=FONTS["small"])

    canvas.create_line(0, top_pad + plot_h, width, top_pad + plot_h, fill=THEME["card_border"])
    return canvas


def create_scrollable_treeview(
    parent,
    columns: List[Tuple[str, str, int]],
    selectmode: str = "browse"
) -> Tuple[ttk.Treeview, tk.Frame]:
    container = tk.Frame(
        parent,
        bg=THEME["card_bg"],
        highlightbackground=THEME["card_border"],
        highlightthickness=1,
    )

    col_ids = [c[0] for c in columns]
    tree = ttk.Treeview(
        container,
        columns=col_ids,
        show="headings",
        selectmode=selectmode,
        style="Custom.Treeview",
    )

    v_scroll = ttk.Scrollbar(
        container, orient="vertical", command=tree.yview,
        style="Vertical.TScrollbar"
    )
    h_scroll = ttk.Scrollbar(
        container, orient="horizontal", command=tree.xview
    )
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    for col_id, col_name, width in columns:
        tree.heading(col_id, text=col_name, anchor="center")
        tree.column(col_id, width=width, anchor="center", minwidth=max(55, width // 2))

    tree.tag_configure("evenrow", background=THEME["table_row_alt"])
    tree.tag_configure("oddrow", background=THEME["card_bg"])

    tree.grid(row=0, column=0, sticky="nsew")
    v_scroll.grid(row=0, column=1, sticky="ns")
    h_scroll.grid(row=1, column=0, sticky="ew")
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    return tree, container
