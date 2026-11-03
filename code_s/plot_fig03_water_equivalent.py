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
DATA_DIR = BASE / "data/fig03_water_equivalent"
OUTPUT_DIR = BASE / "output_s/fig03_water_equivalent"
FIGURE_NAME = "fig03_water_equivalent"
SHOW_FIGURES = True
SAVE_FIGURES = False
FORMATS = ("png", "pdf", "svg")
DPI = 300

import matplotlib.dates as mdates
FONT_FAMILY = "Times New Roman"  # 可修改为其他已安装字体
FONT_SIZE = 8
FIGURE_WIDTH_MM = 183
FIGURE_HEIGHT_IN = 2.8

# x 轴显示范围（北京时间）。None 自动取界，也可只设置一端。
# 使用完整日期时间，例如 "2024-01-17 01:00" 和 "2024-01-17 08:00"。
# 仅改变显示范围；数据仅含默认个例的最终三条曲线。
X_START = "2024-01-17 00:00"
X_END = "2024-01-17 12:00"
X_LABEL = "Time (BJT; UTC+8)"

# 三条线同时用颜色、线型和空心 marker 区分；marker 稀疏显示，曲线保留所有分钟。
# MARKER_EVERY 越小，marker 越密；各线错开位置，降低重叠遮挡。
MARKER_EVERY = 18
RAW_GAUGE_STYLE = {"label": "Uncorrected gauge", "color": "#646464",
                   "linestyle": ":", "linewidth": 1.05, "zorder": 4,
                   "marker": "o", "markersize": 3.0, "markerfacecolor": "none",
                   "markeredgewidth": 0.8, "markevery": (0, MARKER_EVERY)}
CORRECTED_GAUGE_STYLE = {"label": "Corrected gauge", "color": "#D55E00",
                         "linestyle": "--", "linewidth": 1.35, "zorder": 2,
                         "marker": "s", "markersize": 3.6, "markerfacecolor": "none",
                         "markeredgewidth": 0.85, "markevery": (MARKER_EVERY // 3, MARKER_EVERY)}
METHOD_LABEL = "Mass derived with hydrodynamic theory"
METHOD_STYLE = {"color": "#0072B2", "linestyle": "-", "linewidth": 1.15, "zorder": 3,
                "marker": "^", "markersize": 3.7, "markerfacecolor": "none",
                "markeredgewidth": 0.85, "markevery": (2 * MARKER_EVERY // 3, MARKER_EVERY)}


def figure_style():
    return {"font.family": [FONT_FAMILY], "font.size": FONT_SIZE,
            "axes.labelsize": FONT_SIZE + 1, "axes.titlesize": FONT_SIZE + 1,
            "xtick.labelsize": FONT_SIZE, "ytick.labelsize": FONT_SIZE,
            "legend.fontsize": FONT_SIZE, "legend.frameon": False,
            "axes.spines.top": False, "axes.spines.right": False,
            "axes.linewidth": 0.8, "axes.labelpad": 6,
            "xtick.direction": "out", "ytick.direction": "out",
            "xtick.major.size": 3.5, "ytick.major.size": 3.5,
            "xtick.major.width": 0.8, "ytick.major.width": 0.8,
            "lines.solid_capstyle": "round",
            "mathtext.fontset": "custom", "mathtext.rm": FONT_FAMILY,
            "mathtext.it": f"{FONT_FAMILY}:italic", "mathtext.bf": f"{FONT_FAMILY}:bold",
            "mathtext.bfit": f"{FONT_FAMILY}:italic:bold", "mathtext.sf": FONT_FAMILY,
            "mathtext.fallback": "stix", "pdf.fonttype": 42, "svg.fonttype": "none",
            "figure.facecolor": "white", "axes.facecolor": "white"}

class LeftEndpointDateLocator(mdates.AutoDateLocator):
    """保留自动时间刻度，并始终标出当前视窗的左端时间。"""

    def __call__(self):
        ticks = np.asarray(super().__call__())
        left, right = self.axis.get_view_interval()
        # 移除过近的自动刻度，避免左端日期/时间与下一个标签挤在一起。
        min_gap = 0.08 * (right - left)
        ticks = ticks[(ticks - left >= min_gap) & (ticks <= right)]
        return np.concatenate(([left], ticks))

def draw(arrays, settings):
    styles = [RAW_GAUGE_STYLE, CORRECTED_GAUGE_STYLE, {**METHOD_STYLE, "label": METHOD_LABEL}]
    with plt.rc_context(figure_style()):
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH_MM / 25.4, FIGURE_HEIGHT_IN), layout="constrained")
        for series, style in zip(settings["series"], styles):
            for index, prefix in enumerate(series["blocks"]):
                options = dict(style)
                if index:
                    options.pop("label", None)
                ax.plot(arrays[prefix+"_time"], arrays[prefix+"_rate"], **options)
            prefix = series["isolated"]
            if arrays[prefix+"_rate"].size:
                ax.plot(arrays[prefix+"_time"], arrays[prefix+"_rate"],
                        color=style["color"], ls="none", marker=style.get("marker", "o"),
                        ms=style.get("markersize", 2.5),
                        markerfacecolor=style.get("markerfacecolor", "none"),
                        markeredgecolor=style.get("markeredgecolor", style["color"]),
                        markeredgewidth=style.get("markeredgewidth", .8), zorder=style.get("zorder",2))
        ax.set(xlabel=X_LABEL, ylabel="SR (mm h⁻¹)")
        ax.margins(x=0, y=.08)
        if X_START is not None or X_END is not None:
            first_time = min(value.min() for key,value in arrays.items() if key.endswith("_time") and value.size)
            last_time = max(value.max() for key,value in arrays.items() if key.endswith("_time") and value.size)
            ax.set_xlim(np.datetime64(X_START) if X_START is not None else first_time,
                        np.datetime64(X_END) if X_END is not None else last_time)
        locator = LeftEndpointDateLocator(minticks=4, maxticks=8, tz="UTC")
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz="UTC"))
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#E6E6E6", linewidth=.55)
        ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(.5,1.02),
                  borderaxespad=0, handlelength=3, handletextpad=.6, columnspacing=1.3, numpoints=1)
    return fig, ax


def load_data(root):
    """Read final curves; preserve original block/isolated-point order and missing values."""
    with (root / "series.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    arrays, series = {}, []
    for series_id in range(3):
        selected = [row for row in rows if int(row["series_id"]) == series_id]
        blocks = sorted({int(row["block_id"]) for row in selected if row["is_isolated"] == "0"})
        prefixes = []
        for block_id in blocks:
            group = [row for row in selected if row["is_isolated"] == "0" and int(row["block_id"]) == block_id]
            prefix = f"series_{series_id}_block_{block_id}"
            arrays[prefix+"_time"] = np.asarray([row["time_bjt"] for row in group], dtype="datetime64[ns]")
            arrays[prefix+"_rate"] = np.asarray([float(row["rate_mm_h"]) for row in group], dtype=np.float64)
            prefixes.append(prefix)
        prefix = f"series_{series_id}_isolated"
        group = [row for row in selected if row["is_isolated"] == "1"]
        arrays[prefix+"_time"] = np.asarray([row["time_bjt"] for row in group], dtype="datetime64[ns]")
        arrays[prefix+"_rate"] = np.asarray([float(row["rate_mm_h"]) for row in group], dtype=np.float64)
        series.append({"blocks": prefixes, "isolated": prefix})
    return arrays, {"series": series}


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
