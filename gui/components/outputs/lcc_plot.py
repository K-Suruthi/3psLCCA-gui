"""
gui/components/outputs/lcc_plot.py

Creates a matplotlib Figure from LCC analysis results.
Call create_lcc_figure(results) to get a Figure ready to embed in Qt.
"""

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PySide6.QtWidgets import QApplication


def M(x):
    """Convert to Million INR."""
    return x / 1e6


def sci_label(x):
    if x == 0:
        return "0"
    exp = int(np.floor(np.log10(abs(x))))
    coeff = x / (10 ** exp)
    return rf"${coeff:.0f}\cdot10^{{{exp}}}$"


def _get(d, *keys, default=0.0):
    """Safe nested dict access."""
    node = d
    for k in keys:
        if not isinstance(node, dict):
            return default
        node = node.get(k, default)
    return node if node is not None else default


def create_lcc_figure(results: dict) -> plt.Figure:
    """
    Build and return a matplotlib Figure from LCC results dict.
    Embed in Qt via FigureCanvasQTAgg(create_lcc_figure(results)).
    """
    # ── Read OS/app palette for text and background colors ─────────────────
    palette = QApplication.instance().palette()
    text_color = palette.windowText().color().name()
    bg_color   = palette.window().color().name()

    values = [
        # ── Initial stage ──────────────────────────────────────────────────
        M(_get(results, "initial_stage", "economic",     "initial_construction_cost")),
        M(_get(results, "initial_stage", "environmental","initial_material_carbon_emission_cost")),
        M(_get(results, "initial_stage", "economic",     "time_cost_of_loan")),
        M(_get(results, "initial_stage", "social",       "initial_road_user_cost")),
        M(_get(results, "initial_stage", "environmental","initial_vehicular_emission_cost")),

        # ── Use stage ──────────────────────────────────────────────────────
        M(_get(results, "use_stage", "economic",     "routine_inspection_costs")),
        M(_get(results, "use_stage", "economic",     "periodic_maintenance")),
        M(_get(results, "use_stage", "environmental","periodic_carbon_costs")),
        M(_get(results, "use_stage", "economic",     "major_inspection_costs")),
        M(_get(results, "use_stage", "economic",     "major_repair_cost")),
        M(_get(results, "use_stage", "environmental","major_repair_material_carbon_emission_costs")),
        M(_get(results, "use_stage", "environmental","major_repair_vehicular_emission_costs")),
        M(_get(results, "use_stage", "social",       "major_repair_road_user_costs")),
        M(_get(results, "use_stage", "economic",     "replacement_costs_for_bearing_and_expansion_joint")),
        M(_get(results, "use_stage", "environmental","vehicular_emission_costs_for_replacement_of_bearing_and_expansion_joint")),
        M(_get(results, "use_stage", "social",       "road_user_costs_for_replacement_of_bearing_and_expansion_joint")),

        # ── End-of-life stage ──────────────────────────────────────────────
        M(_get(results, "end_of_life", "economic",     "total_demolition_and_disposal_costs")),
        M(_get(results, "end_of_life", "environmental","carbon_costs_demolition_and_disposal")),
        M(_get(results, "end_of_life", "environmental","demolition_vehicular_emission_cost")),
        M(_get(results, "end_of_life", "social",       "ruc_demolition")),
        -M(_get(results, "end_of_life", "economic",    "total_scrap_value")),
    ]

    labels = [
        "Initial construction\ncost",
        "Initial carbon\nemission cost",
        "Time-related\ncost",
        "Road user cost\n(construction)",
        "Vehicular emission\n(rerouting)",

        "Routine inspection\ncost",
        "Periodic maintenance\ncost",
        "Maintenance carbon\ncost",
        "Major inspection\ncost",
        "Major repair\ncost",
        "Repair carbon\nemission cost",
        "Repair vehicular\nemission cost",
        "Road user cost\n(repairs)",
        "Bearing & joint\nreplacement cost",
        "Vehicular emission\n(replacement)",
        "Road user cost\n(replacement)",

        "Demolition &\ndisposal cost",
        "Demolition carbon\ncost",
        "Vehicular emission\n(demolition)",
        "Road user cost\n(demolition)",
        "Scrap value\n(credit)",
    ]

    x = np.arange(len(labels))
    width = 0.50

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.tick_params(colors=text_color)
    ax.yaxis.label.set_color(text_color)
    for spine in ax.spines.values():
        spine.set_edgecolor(text_color)

    # ── Stage background panels ────────────────────────────────────────────
    ax.axvspan(-0.5,  4.5, color="#cfd9e8", alpha=0.9)
    ax.axvspan( 4.5, 15.5, color="#cfe8e2", alpha=0.9)
    ax.axvspan(15.5, len(labels) - 0.5, color="#edd5d5", alpha=0.9)

    # ── Bars ──────────────────────────────────────────────────────────────
    bar_colors = ["#8b1a1a" if v >= 0 else "#2e7d32" for v in values]
    bars = ax.bar(x, values, width, color=bar_colors)

    # ── Stage dividers ─────────────────────────────────────────────────────
    ax.axvline(4.5,  color="black", linewidth=1.5)
    ax.axvline(15.5, color="black", linewidth=1.5)
    ax.axhline(0,    color="black", linewidth=0.8)

    # ── Stage titles ───────────────────────────────────────────────────────
    for center, label in [
        ((0 + 4) / 2,   "Initial Stage"),
        ((5 + 15) / 2,  "Use Stage"),
        ((16 + 20) / 2, "End-of-Life Stage"),
    ]:
        ax.text(center, 1.02, label,
                transform=ax.get_xaxis_transform(),
                ha="center", va="bottom", fontsize=8, fontweight="bold",
                color=text_color)

    # ── Bar value labels ───────────────────────────────────────────────────
    ylim_top = max(max(values) * 1.3, 1.0)
    ax.set_ylim(min(min(values) * 1.3, -0.5), ylim_top)

    for bar, val in zip(bars, values):
        lbl = sci_label(val) if abs(val) < 0.1 else f"{val:.2f}"
        y_pos = val + ylim_top * 0.02 if val >= 0 else val - ylim_top * 0.05
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y_pos,
            lbl,
            ha="center", va="bottom" if val >= 0 else "top",
            rotation=90, fontsize=7,
            color=bar.get_facecolor(),
        )

    # ── Axes styling ──────────────────────────────────────────────────────
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=90, fontsize=6, color=text_color)
    ax.set_ylabel("Cost (Million INR)", fontsize=8, color=text_color)
    ax.tick_params(axis='y', labelsize=7, colors=text_color)
    ax.tick_params(axis='x', colors=text_color)
    ax.axhline(0, color=text_color, linewidth=0.8)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.set_xlim(-0.5, len(labels) - 0.5)

    # Colour x-axis labels by stage
    for i, lbl in enumerate(ax.get_xticklabels()):
        lbl.set_color("#2c4a75" if i <= 4 else "#1f6f66" if i <= 15 else "#7a3b3b")

    # ── Warnings banner ────────────────────────────────────────────────────
    warnings = results.get("warnings", [])
    if warnings:
        fig.text(0.5, 0.01, "⚠ " + " | ".join(warnings),
                 ha="center", fontsize=8, color="#856404",
                 bbox=dict(boxstyle="round", fc="#fff3cd", ec="#ffc107"))

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.40, top=0.88)
    return fig
