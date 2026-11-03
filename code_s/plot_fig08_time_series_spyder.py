"""图08：读取默认图的最终数值，在 Spyder 中可修改下方字体、颜色、画布后 F5。
固定：2024-01-17_E01，390 m，直接质量方案，T-matrix，几何订正。
CSV 只包含实际绘制的 dBZ、误差棒边界和时间；NaN 保留缺测断线。
"""
from __future__ import annotations

# %% 字体、画布和输出参数
SHOW_FIGURE = True
SAVE_FIGURE = False
FORMATS = ("png", "pdf", "svg")
DPI = 300
FIGURE_SIZE_MM = (180, 128)
FONT_FAMILY = "Times New Roman"    # 可改为 "Arial"、"Calibri" 等已安装字体
FONT_SIZE = 10                    # 基础字号，同时控制刻度字号，单位pt
LABEL_FONT_SIZE = FONT_SIZE + 1   # x、y轴标题字号
LEGEND_FONT_SIZE = 8              # 图例字号，可独立修改
PANEL_LABEL_FONT_SIZE = 11        # (a)、(b)字号
PANEL_LABEL_POSITION = (.02, .98) # 子图内部左上，坐标范围0–1
LEGEND_NCOL = 6                   # 优先一行；容不下时自动减少列数，不缩小字体
LEGEND_GAP_MM = 3.0               # b的刻度/x轴标题下缘至图例上缘的净距离；越大越远
LEGEND_BOTTOM_MM = 3.0            # 图例下缘距整张图片底边的距离
SUBPLOT_HSPACE = .18              # 两子图之间的距离，相对于子图高度
PLOT_LEFT = .13                   # 两子图和图例共用左右边界，整图比例
PLOT_RIGHT = .98
PLOT_TOP = .97
Y_LIMITS = {"Ka": None, "W": None}  # e.g. {"Ka": (-40, 30), "W": (-50, 20)}
OUTPUT_DIRECTORY = None            # None -> manuscript_plot/output_s/fig08_time_series

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
from datetime import datetime, timezone, timedelta
import math
import matplotlib.dates as mdates

DATA_DIR = BASE / "data/fig08_time_series"
FIGURE_INFO = {
    "figure": "08", "event_id": "2024-01-17_E01", "height_m": 390,
    "method": "tmatrix", "geometry_correction": True, "window_minutes": 5,
    "time_axis": "Beijing time UTC+8; five-minute window start",
    "values": "Final displayed dBZ; NaN preserves missing observations and curve gaps",
    "errorbars": "Native accepted-sample min/max within the five-minute window",
    "geometry": "Geometry-corrected diagnostic values, including windows beyond the formal 5 dB validity limit",
}
BJT = timezone(timedelta(hours=8))
ASPECT_RATIOS = (.2, .4, .6, .8, 1.)
COLORS = {.2: "#D73027", .4: "#E68A00", .6: "#20864A", .8: "#7B4DA0", 1.: "#2874B8"}
LINESTYLES = {.2: "-", .4: "--", .6: "-.", .8: ":", 1.: (0, (5, 1, 1, 1))}

def _time_axis(axis, times):
    hours = (times[-1]-times[0])/3600 if len(times) > 1 else 0
    locator = (mdates.HourLocator(interval=max(1, math.ceil(hours/6)), tz=BJT) if hours > 3 else
               mdates.MinuteLocator(byminute=list(range(0, 60, 30 if hours > 1 else 10)), tz=BJT))
    axis.xaxis.set_major_locator(locator)
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=BJT))
    axis.grid(axis="y", color="#D9D9D9", linewidth=.45)


def _line_with_gaps(stamps, values):
    """Insert only a NaN break if an entire 5 min clock row is absent."""
    times, result = [], []
    for index, (stamp, value) in enumerate(zip(stamps, values)):
        if index and stamp-stamps[index-1] > 300.001:
            times.append(datetime.fromtimestamp(stamps[index-1]+300, BJT))
            result.append(np.nan)
        times.append(datetime.fromtimestamp(stamp, BJT))
        result.append(value)
    return times, result


def figure_style():
    """Keep ordinary text and mathematical labels in the selected font family."""
    return {"font.family": [FONT_FAMILY], "font.size": FONT_SIZE,
        "axes.labelsize": LABEL_FONT_SIZE, "axes.titlesize": FONT_SIZE,
        "legend.fontsize": LEGEND_FONT_SIZE,
        "xtick.labelsize": FONT_SIZE, "ytick.labelsize": FONT_SIZE,
        "mathtext.fontset": "custom", "mathtext.rm": FONT_FAMILY,
        "mathtext.it": f"{FONT_FAMILY}:italic", "mathtext.bf": f"{FONT_FAMILY}:bold",
        "mathtext.bfit": f"{FONT_FAMILY}:italic:bold", "mathtext.sf": FONT_FAMILY,
        "mathtext.fallback": "stix", "svg.fonttype": "none", "pdf.fonttype": 42,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": .7, "legend.frameon": False}


def bottom_legend(fig, axes, handles, labels):
    """Align the shared legend to both axes, reserving a measured label-to-legend gap."""
    if (isinstance(LEGEND_NCOL, bool) or int(LEGEND_NCOL) != LEGEND_NCOL
            or LEGEND_NCOL < 1 or not np.isfinite([LEGEND_GAP_MM, LEGEND_BOTTOM_MM]).all()
            or LEGEND_GAP_MM < 0 or LEGEND_BOTTOM_MM < 0):
        raise ValueError("LEGEND_NCOL须为正整数；图例间距须为非负有限数。")
    height_mm = fig.get_figheight() * 25.4
    width = PLOT_RIGHT - PLOT_LEFT
    common = dict(handlelength=2.2, columnspacing=1.0, handletextpad=.45,
                  fontsize=LEGEND_FONT_SIZE, borderaxespad=0, borderpad=0,
                  frameon=False, labelspacing=.45)
    columns = min(int(LEGEND_NCOL), len(labels))
    while True:
        probe = fig.legend(handles, labels, loc="lower left", ncol=columns, **common)
        fig.canvas.draw()
        fits = probe.get_window_extent(fig.canvas.get_renderer()).width <= width * fig.bbox.width
        probe.remove()
        if fits:
            break
        if columns == 1:
            raise ValueError("图例文字宽于绘图区，请减小LEGEND_FONT_SIZE或增大FIGURE_SIZE_MM宽度。")
        columns -= 1
    legend = fig.legend(handles, labels, loc="lower left", ncol=columns, mode="expand",
                        bbox_to_anchor=(PLOT_LEFT, LEGEND_BOTTOM_MM / height_mm, width, 0),
                        bbox_transform=fig.transFigure, **common)
    # Reposition both axes together; keep the legend at the bottom of the figure.
    for _ in range(2):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        target_y = legend.get_window_extent(renderer).y1 + LEGEND_GAP_MM / height_mm * fig.bbox.height
        bottom = fig.subplotpars.bottom + (target_y - axes[-1].get_tightbbox(renderer).y0) / fig.bbox.height
        if bottom >= PLOT_TOP - .35:
            raise ValueError("字号/图例间距占用过多高度，请增大FIGURE_SIZE_MM高度或减小字号、间距。")
        fig.subplots_adjust(bottom=bottom)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    legend_box = legend.get_window_extent(renderer)
    measured_gap = (axes[-1].get_tightbbox(renderer).y0 - legend_box.y1) / fig.bbox.height * height_mm
    return {"columns": columns, "gap_mm": float(measured_gap),
            "bottom_mm": LEGEND_BOTTOM_MM,
            "bounds_figure": list(legend_box.transformed(fig.transFigure.inverted()).bounds)}


def load_data(data_dir=None):
    root = Path(data_dir or DATA_DIR)
    with (root / "plot_values.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        data = {key: np.array([float(row[key]) for row in rows]) for key in reader.fieldnames}
    info = dict(FIGURE_INFO, clock_windows=len(rows), aspect_ratios=list(ASPECT_RATIOS))
    return data, info


def draw(data):
    mpl.rcParams.update(figure_style())
    stamps = data['time_epoch_s']
    datetimes = np.array([datetime.fromtimestamp(t, BJT) for t in stamps])
    fig, axes = plt.subplots(2, 1,
        figsize=(FIGURE_SIZE_MM[0] / 25.4, FIGURE_SIZE_MM[1] / 25.4), sharex=True)
    for panel, (ax, band) in enumerate(zip(axes, ("Ka", "W"))):
        mean, lower, upper = (data[band + suffix] for suffix in ("_mean", "_lower", "_upper"))
        display = np.isfinite(mean) & np.isfinite(lower) & np.isfinite(upper)
        if display.any():
            yerr = np.vstack((np.maximum(0, mean[display] - lower[display]),
                             np.maximum(0, upper[display] - mean[display])))
            ax.errorbar(datetimes[display], mean[display], yerr=yerr,
                color="black", ecolor="#454545", fmt="o", markersize=2.3,
                linewidth=.65, elinewidth=.5, capsize=1.3, label="MWII", zorder=6)
        else:
            ax.plot([], [], "o", color="black", markersize=2.5, label="MWII")
        models = []
        for ratio in ASPECT_RATIOS:
            values = data[f"{band}_r{int(round(ratio * 10)):02d}"]
            models.append(values)
            line_times, line_values = _line_with_gaps(stamps, values)
            ax.plot(line_times, line_values, color=COLORS[ratio], linestyle=LINESTYLES[ratio],
                    linewidth=.85, marker=".", markersize=2, markeredgewidth=0,
                    label=f"r = {ratio:.1f}", zorder=3)
        if not display.any():
            ax.set_title("No radar window passes coverage/QC", loc="left",
                         fontsize=FONT_SIZE - 1, pad=6, color="#555555")
        elif not any(np.isfinite(values).any() for values in models):
            ax.set_title("No valid model curve for this window set", loc="left",
                         fontsize=FONT_SIZE - 1, pad=6, color="#555555")
        ax.set_ylabel(rf"$Z_{{e,\mathrm{{{band}}}}}$ (dBZ)")
        ax.text(*PANEL_LABEL_POSITION, f"({chr(ord('a') + panel)})", transform=ax.transAxes,
                fontsize=PANEL_LABEL_FONT_SIZE, fontweight="bold", va="top", ha="left")
        if Y_LIMITS[band] is not None:
            ax.set_ylim(*Y_LIMITS[band])
        _time_axis(ax, stamps)
        ax.margins(x=.02, y=.12)
    handles, labels = axes[0].get_legend_handles_labels()
    order = sorted(range(len(labels)), key=lambda i: 0 if labels[i] == "MWII" else 1)
    axes[-1].set_xlabel("Time (BJT; UTC+8)")
    axes[-1].set_xlim(datetime.fromtimestamp(stamps[0] - 150, BJT),
                      datetime.fromtimestamp(stamps[-1] + 300, BJT))
    fig.subplots_adjust(left=PLOT_LEFT, right=PLOT_RIGHT, top=PLOT_TOP, bottom=.2,
                        hspace=SUBPLOT_HSPACE)
    bottom_legend(fig, axes, [handles[i] for i in order], [labels[i] for i in order])
    return fig, axes


def main(show=SHOW_FIGURE, save=SAVE_FIGURE, data_dir=None, output_directory=None):
    """Read final plotted numbers; show/save the frozen default figure."""
    data, info = load_data(data_dir)
    fig, axes = draw(data)
    if save:
        output = Path(output_directory or OUTPUT_DIRECTORY or BASE / "output_s/fig08_time_series")
        output.mkdir(parents=True, exist_ok=True)
        for extension in FORMATS:
            if extension not in {"png", "pdf", "svg"}:
                raise ValueError("FORMATS supports png, pdf and svg")
            fig.savefig(output / f"fig08_time_series.{extension}", dpi=DPI, facecolor="white")
    if show and mpl.get_backend().lower() != "agg":
        plt.show()
    elif not show:
        plt.close(fig)
    return fig, axes, data, info


def run(show=None, save=None, data_dir=None, output_dir=None):
    return main(show=SHOW_FIGURE if show is None else show,
                save=SAVE_FIGURE if save is None else save,
                data_dir=data_dir, output_directory=output_dir)


if __name__ == "__main__":
    FIGURE, AXES, PLOT_DATA, FIGURE_INFO = main()
