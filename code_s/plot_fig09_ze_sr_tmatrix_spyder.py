"""图09：只读取默认图的最终散点和已完成的拟合结果。
固定：1 min，默认密度关系，T-matrix，轴比0.2。
字体、字号、散点、线条、图例和输出参数均可在下方修改。
"""
from __future__ import annotations

# %% 字体与画布（单位：字号 pt；画布 mm）
FONT_FAMILY = "Times New Roman"   # 可换为其他已安装字体，如 "Arial"
FONT_SIZE = 10
LABEL_FONT_SIZE = FONT_SIZE + 1
LEGEND_FONT_SIZE = 9
FIT_FONT_SIZE = 10
FIGURE_SIZE_MM = (180, 150)
PLOT_MARGINS = dict(left=0.15, right=0.97, bottom=0.13, top=0.975)

# %% 散点、拟合线及图例
KA_COLOR = "#2166AC"
W_COLOR = "#B35806"
KA_MARKER_SIZE = 14
W_MARKER_SIZE = 11
KA_ALPHA = 0.4
W_ALPHA = 0.27
FIT_LINE_WIDTH = 2.0
LEGEND_LOCATION = "upper left"
LEGEND_MARKER_SCALE = 1.6
SHOW_FIT_EQUATIONS = True
FIT_TEXT_X = 0.975
FIT_TEXT_Y = {"Ka": 0.125, "W": 0.052}  # 轴内相对位置，0=底部，1=顶部
SR_LIMITS = None                 # None 自动；例：(1e-5, 10)
ZE_LIMITS = None                 # None 自动；例：(1e-5, 1e3)
# 修改显示范围不改变拟合样本。Ze 使用线性值 mm^6 m^-3，双对数坐标。

# %% 输出
SHOW_FIGURE = True
SAVE_FIGURE = False
FORMATS = ("png", "pdf", "svg")
DPI = 300
OUTPUT_DIRECTORY = None         # None -> manuscript_plot/output_s/fig09_ze_sr_tmatrix


from pathlib import Path
import csv
import os
import sys
import numpy as np
import matplotlib as mpl

if not ("ipykernel" in sys.modules or "spyder_kernels" in sys.modules
        or any(key.startswith("SPYDER") for key in os.environ)):
    mpl.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[1]
from matplotlib import font_manager
from matplotlib.ticker import LogLocator, NullFormatter

DATA_DIR = BASE / "data/fig09_ze_sr_tmatrix"
FIGURE_INFO = {
    "figure": "09", "interval_minutes": 1, "aspect_ratio": .2,
    "method": "tmatrix", "psd": "Gamma M234",
    "values": "Final common positive SR (mm/h) and linear Ze (mm^6/m^3), in original draw order",
}

def number(row, key):
    return float(row[key])


def load_data(data_dir=None):
    root = Path(data_dir or DATA_DIR)
    with (root / "plot_values.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        rows = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]
    with (root / "fits.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        fits = {row["band"]: {
            "valid": row["valid"].strip().lower() == "true",
            "a": float(row["a"]), "b": float(row["b"]),
            "r_squared_log": float(row["r_squared_log"]) if row["r_squared_log"] else None,
        } for row in csv.DictReader(stream)}
    info = dict(FIGURE_INFO, displayed_samples=len(rows), fits=fits)
    return rows, info



def decade_limits(values):
    values = np.asarray(values)
    lo, hi = np.floor(np.log10(values.min())), np.ceil(np.log10(values.max()))
    if lo == hi:
        lo, hi = lo - 1, hi + 1
    return 10.**lo, 10.**hi


def validate_limits(limits, name):
    if limits is not None and (len(limits) != 2 or not np.isfinite(limits).all()
                               or not 0 < limits[0] < limits[1]):
        raise ValueError(name + " must be None or two increasing positive finite values")


def draw(kept, fits):
    if not kept:
        raise ValueError("No complete positive common Ka/W windows; no log plot or fabricated fit produced")
    validate_limits(SR_LIMITS, "SR_LIMITS")
    validate_limits(ZE_LIMITS, "ZE_LIMITS")
    if min(FONT_SIZE, LABEL_FONT_SIZE, LEGEND_FONT_SIZE, FIT_FONT_SIZE) <= 0:
        raise ValueError("Font sizes must be positive")
    font_path = font_manager.findfont(font_manager.FontProperties(family=FONT_FAMILY), fallback_to_default=False)
    style = {"font.family": FONT_FAMILY, "font.size": FONT_SIZE,
        "axes.labelsize": LABEL_FONT_SIZE, "xtick.labelsize": FONT_SIZE, "ytick.labelsize": FONT_SIZE,
        "legend.fontsize": LEGEND_FONT_SIZE, "mathtext.fontset": "custom",
        "mathtext.rm": FONT_FAMILY, "mathtext.it": FONT_FAMILY + ":italic",
        "mathtext.bf": FONT_FAMILY + ":bold", "mathtext.bfit": FONT_FAMILY + ":italic:bold",
        "mathtext.sf": FONT_FAMILY, "mathtext.fallback": "stix", "text.usetex": False,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none", "axes.linewidth": .9,
        "axes.spines.top": True, "axes.spines.right": True,
        "xtick.direction": "in", "ytick.direction": "in", "axes.axisbelow": True}
    # Keep the selected mathematical fonts during later interactive Spyder redraws.
    mpl.rcParams.update(style)
    sr = np.array([number(row, 'sr_mm_h') for row in kept])
    y_values = []
    with mpl.rc_context(style):
        fig, ax = plt.subplots(figsize=(FIGURE_SIZE_MM[0] / 25.4, FIGURE_SIZE_MM[1] / 25.4))
        fig.subplots_adjust(**PLOT_MARGINS)
        ax.set_xscale("log")
        ax.set_yscale("log")
        for band, color, line_style in (("Ka", KA_COLOR, "-"), ("W", W_COLOR, "--")):
            ze = np.array([number(row, f"ze_{band}_mm6_m3") for row in kept])
            y_values.append(ze)
            ax.scatter(sr, ze, s=KA_MARKER_SIZE if band == "Ka" else W_MARKER_SIZE,
                facecolors="none" if band == "Ka" else color, edgecolors=color,
                linewidths=.5 if band == "Ka" else 0, alpha=KA_ALPHA if band == "Ka" else W_ALPHA,
                label=f"{band} {34.96 if band == 'Ka' else 94.5:g} GHz", rasterized=True, zorder=2)
            fit = fits[band]
            if fit["valid"]:
                xfit = np.geomspace(sr.min(), sr.max(), 300)
                yfit = fit["a"] * xfit**fit["b"]
                y_values.append(yfit)
                ax.plot(xfit, yfit, color=color, linestyle=line_style, lw=FIT_LINE_WIDTH, zorder=4)
                r2 = f"{fit['r_squared_log']:.3f}" if fit["r_squared_log"] is not None else "undefined"
                # Scientific notation avoids falsely rounding small a to 0.00.
                coefficient = f"{fit['a']:.2f}" if .01 <= fit['a'] < 1e5 else f"{fit['a']:.3g}"
                # label = (rf"$Z_{{e,\mathrm{{{band}}}}}={coefficient}\,SR^{{{fit['b']:.3f}}}$"
                #          + rf"   ($R^2_{{\mathrm{{log}}}}$={r2})")
                label = (rf"$Z_{{e,\mathrm{{{band}}}}}={coefficient}\,SR^{{{fit['b']:.3f}}}$"
                         )
            else:
                label = f"{band}: insufficient varied samples for fit"
            if SHOW_FIT_EQUATIONS:
                ax.text(FIT_TEXT_X, FIT_TEXT_Y[band], label, transform=ax.transAxes,
                        ha="right", va="bottom", color=color, fontsize=FIT_FONT_SIZE,
                        bbox=dict(facecolor="white", edgecolor="none", alpha=.88, pad=2), zorder=5)
        ax.set_xlim(SR_LIMITS if SR_LIMITS is not None else decade_limits(sr))
        ax.set_ylim(ZE_LIMITS if ZE_LIMITS is not None else decade_limits(np.concatenate(y_values)))
        ax.set_xlabel(r"$SR$ (mm h$^{-1}$)")
        ax.set_ylabel(r"$Z_e$ (mm$^6$ m$^{-3}$)")
        for axis in (ax.xaxis, ax.yaxis):
            axis.set_major_locator(LogLocator(base=10, numticks=20))
            axis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10), numticks=100))
            axis.set_minor_formatter(NullFormatter())
        ax.grid(which="major", color=".78", lw=.5, linestyle="--")
        ax.grid(which="minor", color=".90", lw=.35, linestyle=":")
        ax.legend(loc=LEGEND_LOCATION, frameon=True, facecolor="white", edgecolor="none",
                  markerscale=LEGEND_MARKER_SCALE)
        # No title, subtitle, or figure footnotes.
        fig.canvas.draw()
    return fig, ax, kept, fits, font_path, style

def main(show=SHOW_FIGURE, save=SAVE_FIGURE, data_dir=None, output_directory=None):
    """Read final plotted numbers; show/save the frozen default figure."""
    data, info = load_data(data_dir)
    fig, ax, kept, fits, font_path, style = draw(data, info["fits"])
    if save:
        output = Path(output_directory or OUTPUT_DIRECTORY or BASE / "output_s/fig09_ze_sr_tmatrix")
        output.mkdir(parents=True, exist_ok=True)
        for extension in FORMATS:
            if extension not in {"png", "pdf", "svg"}:
                raise ValueError("FORMATS supports png, pdf and svg")
            fig.savefig(output / f"fig09_ze_sr_tmatrix.{extension}", dpi=DPI, facecolor="white")
    if show and mpl.get_backend().lower() != "agg":
        plt.show()
    elif not show:
        plt.close(fig)
    return fig, ax, data, info


def run(show=None, save=None, data_dir=None, output_dir=None):
    return main(show=SHOW_FIGURE if show is None else show,
                save=SAVE_FIGURE if save is None else save,
                data_dir=data_dir, output_directory=output_dir)


if __name__ == "__main__":
    FIGURE, AXES, PLOT_DATA, FIGURE_INFO = main()
