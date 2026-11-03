# -*- coding: utf-8 -*-
"""图06：Gamma参数与降雪率概率网格，独立精简重绘程序。

只读取本图CSV中的最终绘图数值；未包含原始分钟数据、PSD或分析程序。
数据固定为原程序默认分析结果。可修改字体、尺寸、颜色和绘图语句。
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# %% 可修改的外观和导出参数
DATA_DIR = Path(__file__).resolve().parents[1] / "data/fig06_gamma_sr_ze"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output_s/fig06_gamma_sr_ze"
SHOW_FIGURES = True
SAVE_FIGURES = False
FORMATS = ("png", "pdf", "svg")
DPI = 300
FONT_FAMILY = 'Times New Roman'
FONT_SIZE = 10
COLORBAR_FONT_SIZE = 9
FIGURE_WIDTH_MM = 183
FIGURE_HEIGHT_IN = 3.5
PANEL_AXES = {'a': {'xlim': (0, 6), 'ylim': (-5, 30)}, 'b': {'xlim': (0, 6), 'ylim': (-5, 50)}, 'c': {'xlim': (0, 6), 'ylim': (0, 20)}}
X_MINOR_TICK_INTERVAL = 0.5
PROBABILITY_CMAP = 'jet'
COLORBAR_LIMITS = (0, 3)
COLORBAR_PAD = 0.03
AXIS_TICK_FORMAT = '{x:g}'
COLORBAR_TICK_FORMAT = '{x:.3g}'

def figure_style():
    return {**{'font.sans-serif': ['DejaVu Sans', 'Arial'], 'legend.fontsize': 7, 'axes.linewidth': 0.7, 'lines.linewidth': 1.2, 'legend.frameon': False, 'savefig.dpi': 300, 'figure.facecolor': 'white', 'axes.facecolor': 'white'}, "font.family": [FONT_FAMILY], "font.size": FONT_SIZE,
            "axes.labelsize": FONT_SIZE + 1, "axes.titlesize": FONT_SIZE + .8,
            "xtick.labelsize": FONT_SIZE, "ytick.labelsize": FONT_SIZE,
            "axes.spines.top": False, "axes.spines.right": False,
            "mathtext.fontset": "custom", "mathtext.rm": FONT_FAMILY,
            "mathtext.it": f"{FONT_FAMILY}:italic", "mathtext.bf": f"{FONT_FAMILY}:bold",
            "mathtext.bfit": f"{FONT_FAMILY}:italic:bold", "mathtext.sf": FONT_FAMILY,
            "mathtext.fallback": "stix", "pdf.fonttype": 42, "svg.fonttype": "none"}

def load_data(data_dir=None):
    """edges.csv的列为SR、μ、Λ、log10(N0)边界；三个概率矩阵以x箱为行、y箱为列。

    概率单位为%；空白绘图格以NaN保存；对应矩阵无需重复存边界。
    """
    root = Path(DATA_DIR if data_dir is None else data_dir)
    def read(filename):
        return np.loadtxt(root / filename, delimiter=",", skiprows=1, dtype=np.float64, encoding="utf-8-sig", ndmin=2)
    edges = read("edges.csv")
    files = ("mu_probability_percent.csv", "lambda_probability_percent.csv", "log10_N0_probability_percent.csv")
    return {"x_edges": np.tile(edges[:, 0], (3, 1)), "y_edges": edges[:, 1:4].T,
            "probability_percent": np.stack([read(name) for name in files])}

def axis_edges(limits, count, np):
    """验证可调范围及格数，按实际绘图变量等距分箱。"""
    from numbers import Integral
    limits = np.asarray(limits, dtype=float)
    if limits.shape != (2,) or not np.isfinite(limits).all() or limits[1] <= limits[0]:
        raise ValueError("坐标范围必须为两个有限且递增的数值")
    if isinstance(count, bool) or not isinstance(count, Integral) or count < 1:
        raise ValueError("BIN_COUNTS的两个格数均须为正整数")
    return np.linspace(*limits, count + 1)

def endpoint_ticks(limits, np, nbins=5):
    """保留自动主刻度并补齐精确端点，移除与端点过近的内部刻度。"""
    from matplotlib.ticker import MaxNLocator
    lo, hi = axis_edges(limits, 1, np)
    automatic = MaxNLocator(nbins=nbins, min_n_ticks=3).tick_values(lo, hi)
    step = float(np.min(np.diff(automatic))) if len(automatic) > 1 else hi - lo
    inner = automatic[(automatic > lo + .4 * step) & (automatic < hi - .4 * step)]
    return np.concatenate(([lo], inner, [hi]))

def draw(data):
    from matplotlib.colors import Normalize
    from matplotlib.ticker import AutoMinorLocator, MultipleLocator, StrMethodFormatter
    positive = data['probability_percent'][np.isfinite(data['probability_percent'])]
    norm = Normalize(*(COLORBAR_LIMITS if COLORBAR_LIMITS is not None else (0, positive.max())))
    lower_clip, upper_clip = bool(positive.min() < norm.vmin), bool(positive.max() > norm.vmax)
    extend = "both" if lower_clip and upper_clip else "min" if lower_clip else "max" if upper_clip else "neither"
    definitions = [("a", "μ"), ("b", "Λ (mm⁻¹)"), ("c", r"$\log_{10} N_0$")]
    with plt.rc_context(figure_style()):
        fig, axs = plt.subplots(1, 3, figsize=(FIGURE_WIDTH_MM / 25.4, FIGURE_HEIGHT_IN), layout="constrained")
        for index, (ax, (name, ylabel)) in enumerate(zip(axs, definitions)):
            mesh = ax.pcolormesh(data["x_edges"][index], data["y_edges"][index], np.ma.masked_invalid(data['probability_percent'][index].T),
                                cmap=PROBABILITY_CMAP, norm=norm, shading="flat", rasterized=True)
            ax.set(xlim=PANEL_AXES[name]["xlim"], ylim=PANEL_AXES[name]["ylim"], xlabel="SR (mm h⁻¹)", ylabel=ylabel, yscale="linear")
            ax.set_xticks(endpoint_ticks(PANEL_AXES[name]["xlim"], np))
            ax.set_yticks(endpoint_ticks(PANEL_AXES[name]["ylim"], np))
            ax.xaxis.set_major_formatter(StrMethodFormatter(AXIS_TICK_FORMAT))
            ax.yaxis.set_major_formatter(StrMethodFormatter(AXIS_TICK_FORMAT))
            ax.set_title(f"({name})", loc="left")
            ax.set_box_aspect(1)
            if X_MINOR_TICK_INTERVAL is not None:
                ax.xaxis.set_minor_locator(MultipleLocator(X_MINOR_TICK_INTERVAL))
            ax.yaxis.set_minor_locator(AutoMinorLocator())
            ax.tick_params(which="minor", length=2.5, width=.7)
        colorbar = fig.colorbar(mesh, ax=axs, orientation="horizontal", extend=extend, pad=COLORBAR_PAD, fraction=.10, aspect=40)
        colorbar.set_ticks(endpoint_ticks((norm.vmin, norm.vmax), np, nbins=6))
        colorbar.formatter = StrMethodFormatter(COLORBAR_TICK_FORMAT)
        colorbar.update_ticks()
        colorbar.set_label("Probability (%)", fontsize=COLORBAR_FONT_SIZE)
        colorbar.ax.tick_params(labelsize=COLORBAR_FONT_SIZE)
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
