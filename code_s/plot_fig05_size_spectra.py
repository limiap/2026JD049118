# -*- coding: utf-8 -*-
"""图05：粒径谱，独立精简重绘程序。

只读取本图CSV中的最终绘图数值；未包含原始分钟数据、PSD或分析程序。
Case分组已按selected_event_final.csv订正，其他统计沿用原默认设置。
可修改字体、尺寸、颜色和绘图语句。
"""
from pathlib import Path
import csv
import re
import numpy as np
import matplotlib.pyplot as plt

# %% 可修改的外观和导出参数
DATA_DIR = Path(__file__).resolve().parents[1] / "data/fig05_size_spectra"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output_s/fig05_size_spectra"
SHOW_FIGURES = True
SAVE_FIGURES = False
FORMATS = ("png", "pdf", "svg")
DPI = 300
FONT_FAMILY = 'Times New Roman'
FONT_SIZE = 10
LEGEND_FONT_SIZE = 7
FIGURE_WIDTH_MM = 183
FIGURE_HEIGHT_IN = 3.3
X_MINOR_TICK_INTERVAL = 0.5
SR_COLORS = ['#0072B2', '#D55E00', '#009E73', '#CC79A7']
SR_LINESTYLES = ['-']
SR_LINEWIDTH = 1.5

# 固定的默认绘图标签（无需单独标签文件）。
SR_GROUP_LABELS = ['0 < SR ≤ 0.1', '0.1 < SR ≤ 1', '1 < SR ≤ 2', 'SR > 2']

def figure_style():
    """沿用 Fig03 的字体、开放边框和可编辑矢量文字。"""
    return {**{'font.sans-serif': ['DejaVu Sans', 'Arial'], 'axes.linewidth': 0.7, 'lines.linewidth': 1.2, 'savefig.dpi': 300, 'figure.facecolor': 'white', 'axes.facecolor': 'white'}, "font.family": [FONT_FAMILY], "font.size": FONT_SIZE,
            "axes.labelsize": FONT_SIZE + 1, "axes.titlesize": FONT_SIZE + .8,
            "xtick.labelsize": FONT_SIZE, "ytick.labelsize": FONT_SIZE,
            "legend.fontsize": LEGEND_FONT_SIZE, "legend.frameon": False,
            "axes.spines.top": False, "axes.spines.right": False,
            "mathtext.fontset": "custom", "mathtext.rm": FONT_FAMILY,
            "mathtext.it": f"{FONT_FAMILY}:italic", "mathtext.bf": f"{FONT_FAMILY}:bold",
            "mathtext.bfit": f"{FONT_FAMILY}:italic:bold", "mathtext.sf": FONT_FAMILY,
            "mathtext.fallback": "stix", "pdf.fonttype": 42, "svg.fonttype": "none"}

def load_data(data_dir=None):
    """按CSV列名识别case均值谱，Case数量和列位置不写死。

    diameter_mm为粒径(mm)；所有谱浓度单位为mm⁻¹ m⁻³。
    NaN保留原对数轴不显示位置；Case编号由case_mean_XX列名给出。
    """
    root = Path(DATA_DIR if data_dir is None else data_dir)
    path = root / "spectra.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        names = next(csv.reader(stream))
    if len(names) != len(set(names)):
        raise ValueError("spectra.csv存在重复列名")
    cases = sorted((name for name in names if re.fullmatch(r"case_mean_\d+", name)),
                   key=lambda name: int(name.rsplit("_", 1)[1]))
    groups = sorted((name for name in names if re.fullmatch(r"sr_group_mean_\d+", name)),
                    key=lambda name: int(name.rsplit("_", 1)[1]))
    if not cases or len(groups) != len(SR_GROUP_LABELS):
        raise ValueError("spectra.csv缺少Case均值谱或SR分组列数与标签不符")
    case_ids = [int(name.rsplit("_", 1)[1]) for name in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("spectra.csv存在重复Case编号")
    values = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64, encoding="utf-8-sig", ndmin=2)
    if values.shape[1] != len(names):
        raise ValueError("spectra.csv列名与数值列数不符")
    columns = {name: values[:, index] for index, name in enumerate(names)}
    return {"diameter_mm": columns["diameter_mm"], "case_mean": np.stack([columns[name] for name in cases]),
            "case_ids": np.asarray(case_ids), "overall_mean": columns["overall_mean"],
            "sr_group_mean": np.stack([columns[name] for name in groups])}

def draw(data):
    from matplotlib.ticker import MultipleLocator
    sizes = data['diameter_mm']
    with plt.rc_context(figure_style()):
        fig, axs = plt.subplots(1, 2, figsize=(FIGURE_WIDTH_MM / 25.4, FIGURE_HEIGHT_IN), sharey=True, layout="constrained")
        for row in data["case_mean"]:
            axs[0].plot(sizes, row, color="#ADB6BF", alpha=.55, lw=.7)
        axs[0].plot(sizes, data["overall_mean"], color="black", lw=1.8, label="Mean")
        for index, (mean, label) in enumerate(zip(data["sr_group_mean"], SR_GROUP_LABELS)):
            axs[1].plot(sizes, mean, label=label, color=SR_COLORS[index % len(SR_COLORS)],
                        ls=SR_LINESTYLES[(index + index // len(SR_COLORS)) % len(SR_LINESTYLES)], lw=SR_LINEWIDTH)
        for label, ax in zip(("a", "b"), axs):
            ax.set(xlabel="Diameter (mm)", ylabel="N(D) (mm⁻¹ m⁻³)", yscale="log", xlim=(0, sizes.max()))
            ax.set_title(f"({label})", loc="left")
            ax.xaxis.set_minor_locator(MultipleLocator(X_MINOR_TICK_INTERVAL))
            ax.tick_params(axis="x", which="minor", bottom=True, length=2.5, width=.7)
            ax.tick_params(axis="y", labelleft=True)
        axs[0].legend(loc="upper right")
        axs[1].legend(loc="upper right", title_fontsize=LEGEND_FONT_SIZE)
        fig.align_xlabels(axs)
    return fig, axs

def run(show=None, save=None, data_dir=None, output_dir=None):
    """重画固定的默认分析结果；返回 Figure 和 Axes。"""
    root = Path(DATA_DIR if data_dir is None else data_dir)
    data = load_data(root)
    fig, axes = draw(data)
    if SAVE_FIGURES if save is None else save:
        output = Path(OUTPUT_DIR if output_dir is None else output_dir)
        output.mkdir(parents=True, exist_ok=True)
        with plt.rc_context(figure_style()):
            stem = Path(__file__).stem
            paths = {"png": output / (stem + ".png"), "pdf": output / (stem + ".pdf"), "svg": output / (stem + ".svg")}
            for extension in FORMATS:
                fig.savefig(paths[extension], dpi=DPI, bbox_inches="tight")
    if SHOW_FIGURES if show is None else show:
        plt.show(block=False)
    return fig, axes


if __name__ == "__main__":
    fig, axes = run()
