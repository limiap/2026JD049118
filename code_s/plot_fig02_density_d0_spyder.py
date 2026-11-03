# -*- coding: utf-8 -*-
"""Independent final-data replot. Open in Spyder and press F5.

Only full-precision CSV final plotting coordinates are read; no particle processing,
scientific fitting, or original analysis table is needed.
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data/fig02_density_d0"
OUTPUT_DIR = BASE / "output_s/fig02_density_d0"
FIGURE_NAME = "fig02_density_d0"
SHOW_FIGURES = True
SAVE_FIGURES = False
FORMATS = ("png", "pdf", "svg")
DPI = 300

from matplotlib import font_manager
FONT_FAMILY = "Times New Roman"
FONT_SIZE = 11
AXIS_FONT_SIZE = None
TICK_FONT_SIZE = None
LEGEND_FONT_SIZE = None
FIGSIZE = (8.4, 6.2)
X_LIMIT = (0, 10)
Y_LIMIT = (0, 1)
LEGEND_COLUMNS = 1
LEGEND_LOCATION = "upper right"
FIT_LINEWIDTH = 2
# Fixed published comparison relations: only these analytical lines are evaluated.
# The observed fit coefficients below are read from completed-fit output; never refitted.
COMPARISON_RELATIONS = [
    dict(label=r"Tao (2021): $0.36D_0^{-1.52}$", coefficient=.36, exponent=-1.52,
         domain=(.5,10.), color="g", linestyle="--", linewidth=1.6),
    dict(label=r"Brandes (2007): $0.178D_0^{-0.922}$", coefficient=.178, exponent=-.922,
         domain=(.5,10.), color="b", linestyle="--", linewidth=1.6),
]

def figure_style():
    return {"font.family": FONT_FAMILY, "font.size": FONT_SIZE,
            "mathtext.fontset": "custom", "mathtext.rm": FONT_FAMILY,
            "mathtext.it": f"{FONT_FAMILY}:italic", "mathtext.bf": f"{FONT_FAMILY}:bold",
            "axes.labelsize": FONT_SIZE + 1 if AXIS_FONT_SIZE is None else AXIS_FONT_SIZE,
            "axes.spines.top": False, "axes.spines.right": False,
            "axes.linewidth": .8, "pdf.fonttype": 42, "svg.fonttype": "none"}

def draw(arrays, settings):
    font_manager.findfont(FONT_FAMILY, fallback_to_default=False)
    values = arrays["bin_values"]
    x, y, sd = values.T
    defined = np.isfinite(sd)
    lower, upper = float(x.min()), float(x.max())
    fit = settings["original_fit"]
    curve_x = np.geomspace(lower, upper, 512)
    curves = [dict(x=curve_x, y=float(fit['alpha_g_cm3'])*curve_x**float(fit["beta"]),
                   kind="fit", color="#000000", linestyle="-", linewidth=FIT_LINEWIDTH,
                   label=(rf"This study: $\rho = {float(fit['alpha_g_cm3']):.4g}"
                          rf"\,D_0^{{{float(fit['beta']):.4f}}}$"))]
    for relation in COMPARISON_RELATIONS:
        lo, hi = max(lower,relation["domain"][0]), min(upper,relation["domain"][1])
        if lo < hi:
            curve_x = np.geomspace(lo,hi,512)
            curves.append(dict(x=curve_x,y=relation["coefficient"]*curve_x**relation["exponent"],
                               kind="comparison", **{key:relation[key] for key in
                               ("label","color","linestyle","linewidth")}))
    with plt.rc_context(figure_style()):
        fig, ax = plt.subplots(figsize=FIGSIZE)
        fig.subplots_adjust(left=.11, right=.97, bottom=.13, top=.95)
        ax.errorbar(x[defined], y[defined], yerr=sd[defined], fmt="none", ecolor="#777777",
                    elinewidth=.9, capsize=3, capthick=.9, zorder=3, label="Mean ± 1 sample SD")
        ax.plot(x, y, ls="none", marker="o", ms=4.5,
                markerfacecolor="none", markeredgecolor="#333333", markeredgewidth=.9,
                zorder=5, label="Bin mean (all bins)")
        handles = []
        for curve in curves:
            line, = ax.plot(curve["x"], curve["y"], color=curve["color"],
                            linestyle=curve["linestyle"],
                            linewidth=FIT_LINEWIDTH if curve["kind"] == "fit" else curve["linewidth"],
                            zorder=6 if curve["kind"] == "fit" else 4, label=curve["label"])
            handles.append(line)
        all_y = np.concatenate([y, y[defined]-sd[defined], y[defined]+sd[defined]]
                               + [curve["y"] for curve in curves])
        all_x = np.concatenate([x]+[curve["x"] for curve in curves])
        ymin, ymax = float(all_y.min()), float(all_y.max())
        span = max(ymax-min(ymin,0), ymax*.1, 1e-6)
        xlim = (0., float(all_x.max())*1.06) if X_LIMIT is None else X_LIMIT
        ylim = (ymin-.06*span if ymin < 0 else 0., ymax+.07*span) if Y_LIMIT is None else Y_LIMIT
        ax.set(xlabel=r"$D_0$ (mm)", ylabel=r"$\rho$ (g cm$^{-3}$)", xlim=xlim, ylim=ylim)
        ax.tick_params(labelsize=FONT_SIZE if TICK_FONT_SIZE is None else TICK_FONT_SIZE)
        ax.grid(color="#E2E2E2", linewidth=.55, alpha=.7)
        ax.set_axisbelow(True)
        ax.legend(handles=handles, loc=LEGEND_LOCATION,
                  ncol=LEGEND_COLUMNS, fontsize=FONT_SIZE-1 if LEGEND_FONT_SIZE is None else LEGEND_FONT_SIZE,
                  frameon=False, handlelength=3, columnspacing=1.5)
    return fig, ax


def load_data(root):
    """Read full-precision final bin statistics and completed-fit coefficients."""
    with (root / "bins.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    arrays = {"bin_values": np.asarray([[float(row[key]) for key in
              ("D0_mm", "rho_g_cm3", "rho_sample_SD_g_cm3")] for row in rows], dtype=np.float64)}
    with (root / "fit.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        fit = next(csv.DictReader(stream))
    return arrays, {"original_fit": {key: float(value) for key,value in fit.items()}}


def run(show=None, save=None, data_dir=None, output_dir=None):
    """Read final numerical data, draw, and optionally export PNG/PDF/SVG."""
    root = Path(DATA_DIR if data_dir is None else data_dir)
    arrays, settings = load_data(root)
    plt.rcParams.update(figure_style())
    fig, axes = draw(arrays, settings)
    if SAVE_FIGURES if save is None else save:
        output = Path(OUTPUT_DIR if output_dir is None else output_dir)
        output.mkdir(parents=True, exist_ok=True)
        with plt.rc_context(figure_style()):
            for extension in FORMATS:
                fig.savefig(output / (FIGURE_NAME + "." + extension), dpi=DPI, bbox_inches="tight")
    if SHOW_FIGURES if show is None else show:
        plt.show(block=False)
    return fig, axes


if __name__ == "__main__":
    fig, axes = run()
