# -*- coding: utf-8 -*-
"""图07：μ–Λ联合分布，独立精简重绘程序。

只读取本图CSV中的最终绘图数值；未包含原始分钟数据、PSD或分析程序。
数据固定为原程序默认分析结果。可修改字体、尺寸、颜色和绘图语句。
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# %% 可修改的外观和导出参数
DATA_DIR = Path(__file__).resolve().parents[1] / "data/fig07_mu_lambda_joint_distribution"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output_s/fig07_mu_lambda_joint_distribution"
SHOW_FIGURES = True
SAVE_FIGURES = False
FORMATS = ("png", "pdf", "svg")
DPI = 300
FONT_FAMILY = 'Times New Roman'
FONT_SIZE = 10
LEGEND_FONT_SIZE = 9
COLORBAR_FONT_SIZE = 9
FIGURE_WIDTH_MM = 183
FIGURE_HEIGHT_IN = 5.1
COLORBAR_LIMITS = (0.0, 1.0)
MU_PROBABILITY_LIMITS = None
LAMBDA_PROBABILITY_LIMITS = None
LAMBDA_MINOR_INTERVAL = 5
MU_MINOR_INTERVAL = 1
PROBABILITY_CMAP = 'jet'
COLORBAR_TICK_FORMAT = '{x:.3g}'
AXIS_TICK_FORMAT = '{x:g}'
LEFT_WIDTH_RATIO = 0.25
BOTTOM_HEIGHT_RATIO = 0.25
MARGINAL_WGAP = 0.01
MARGINAL_HGAP = 0.01
COLORBAR_PAD = 0.035
COLORBAR_WIDTH_RATIO = 0.035
MARGINAL_COLORS = {'mu': '#3975A3', 'lambda': '#E58A35'}
MARGINAL_LINEWIDTH = 1.5
MARGINAL_LINESTYLE = '-'
MARGINAL_FILL = True
MARGINAL_FILL_ALPHA = 0.22
SHOW_FIT = True
FIT_COLOR = '#E31A1C'
FIT_LINEWIDTH = 1.6
FIT_LINESTYLE = '-'
FIT_LEGEND_LOC = 'lower right'

# 固定的默认绘图标签（无需单独标签文件）。
FIT_LABEL = 'This study (mean): $\\mu=-0.004436\\Lambda^2+0.5892\\Lambda-0.08943$'

def figure_style():
    return {"font.family": [FONT_FAMILY], "font.size": FONT_SIZE,
            "axes.labelsize": FONT_SIZE + 1, "axes.titlesize": FONT_SIZE + .8,
            "xtick.labelsize": FONT_SIZE, "ytick.labelsize": FONT_SIZE,
            "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .7,
            "legend.fontsize": LEGEND_FONT_SIZE, "legend.frameon": False,
            "mathtext.fontset": "custom", "mathtext.rm": FONT_FAMILY,
            "mathtext.it": f"{FONT_FAMILY}:italic", "mathtext.bf": f"{FONT_FAMILY}:bold",
            "mathtext.bfit": f"{FONT_FAMILY}:italic:bold", "mathtext.sf": FONT_FAMILY,
            "mathtext.fallback": "stix", "pdf.fonttype": 42, "svg.fonttype": "none",
            "figure.facecolor": "white", "axes.facecolor": "white"}

def load_data(data_dir=None):
    """只读CSV中的最终边界、密度、边缘曲线及拟合曲线；Λ单位mm⁻¹、概率单位%。

    density.csv以Λ箱为行、μ箱为列；相对密度无单位，NaN表示空格。
    """
    root = Path(DATA_DIR if data_dir is None else data_dir)
    def read(filename):
        return np.loadtxt(root / filename, delimiter=",", skiprows=1, dtype=np.float64, encoding="utf-8-sig", ndmin=2)
    edges, marginal, fit = read("edges.csv"), read("marginals.csv"), read("fit.csv")
    return {"lambda_edges": edges[:, 0], "mu_edges": edges[:, 1], "relative_density": read("density.csv"),
            "mu_coordinates": marginal[:, 0], "mu_probability_percent": marginal[:, 1],
            "lambda_coordinates": marginal[:, 2], "lambda_probability_percent": marginal[:, 3],
            "fit_lambda": fit[:, 0], "fit_mu": fit[:, 1]}

def validate_limits(limits, *, probability=False):
    bounds = np.asarray(limits, dtype=float)
    if bounds.shape != (2,) or not np.isfinite(bounds).all() or bounds[1] <= bounds[0]:
        raise ValueError("范围须为两个有限且递增的数值")
    if probability and bounds[0] < 0:
        raise ValueError("概率范围下限不得为负数")
    return bounds

def endpoint_ticks(limits, nbins=6):
    from matplotlib.ticker import MaxNLocator
    lo, hi = validate_limits(limits)
    automatic = MaxNLocator(nbins=nbins, min_n_ticks=3, steps=[1, 2, 2.5, 5, 10]).tick_values(lo, hi)
    step = float(np.min(np.diff(automatic)))
    inner = automatic[(automatic > lo + .4 * step) & (automatic < hi - .4 * step)]
    return np.concatenate(([lo], inner, [hi]))

def probability_limits(values, configured):
    from matplotlib.ticker import MaxNLocator
    if configured is not None:
        return validate_limits(configured, probability=True)
    maximum = float(np.nanmax(values)) if np.isfinite(values).any() else 0.0
    return np.array([0.0, MaxNLocator(nbins=4).tick_values(0, max(1.0, 1.12 * maximum))[-1]])

def draw(data):
    from matplotlib.colors import Normalize
    from matplotlib.ticker import AutoMinorLocator, MultipleLocator, StrMethodFormatter
    xe, ye = data["lambda_edges"], data["mu_edges"]
    relative_density = data["relative_density"]
    norm = Normalize(*(COLORBAR_LIMITS if COLORBAR_LIMITS is not None else (0, 1)))
    positive = relative_density[np.isfinite(relative_density)]
    below, above = bool(positive.min() < norm.vmin), bool(positive.max() > norm.vmax)
    extend = "both" if below and above else "min" if below else "max" if above else "neither"
    curve_lam, curve_mu = data["fit_lambda"], data["fit_mu"]
    marginal_curves = {"mu": (data["mu_coordinates"], data['mu_probability_percent']),
                       "lambda": (data["lambda_coordinates"], data['lambda_probability_percent'])}
    mu_plim = probability_limits(data['mu_probability_percent'], MU_PROBABILITY_LIMITS)
    lambda_plim = probability_limits(data['lambda_probability_percent'], LAMBDA_PROBABILITY_LIMITS)
    with plt.rc_context(figure_style()):
        fig = plt.figure(figsize=(FIGURE_WIDTH_MM / 25.4, FIGURE_HEIGHT_IN), layout="constrained")
        grid = fig.add_gridspec(3, 5, width_ratios=[LEFT_WIDTH_RATIO, MARGINAL_WGAP, 1, COLORBAR_PAD, COLORBAR_WIDTH_RATIO],
                               height_ratios=[1, MARGINAL_HGAP, BOTTOM_HEIGHT_RATIO], wspace=0, hspace=0)
        ax = fig.add_subplot(grid[0, 2])
        left = fig.add_subplot(grid[0, 0], sharey=ax)
        bottom = fig.add_subplot(grid[2, 2], sharex=ax)
        cax = fig.add_subplot(grid[0, 4])
        mesh = ax.pcolormesh(xe, ye, np.ma.masked_invalid(relative_density.T),
                            cmap=PROBABILITY_CMAP, norm=norm, shading="flat", rasterized=True)
        ax.set(xlim=(xe[0], xe[-1]), ylim=(ye[0], ye[-1]), xlabel="Λ (mm⁻¹)", ylabel="μ")
        ax.set_xticks(endpoint_ticks((xe[0], xe[-1])))
        ax.set_yticks(endpoint_ticks((ye[0], ye[-1])))
        ax.xaxis.set_major_formatter(StrMethodFormatter(AXIS_TICK_FORMAT))
        ax.yaxis.set_major_formatter(StrMethodFormatter(AXIS_TICK_FORMAT))
        ax.xaxis.set_minor_locator(MultipleLocator(LAMBDA_MINOR_INTERVAL) if LAMBDA_MINOR_INTERVAL is not None else AutoMinorLocator())
        ax.yaxis.set_minor_locator(MultipleLocator(MU_MINOR_INTERVAL) if MU_MINOR_INTERVAL is not None else AutoMinorLocator())
        if SHOW_FIT:
            ax.plot(curve_lam, curve_mu, color=FIT_COLOR, lw=FIT_LINEWIDTH, ls=FIT_LINESTYLE, label=FIT_LABEL)
        if ax.lines:
            ax.legend(loc=FIT_LEGEND_LOC)
        mu_coordinates, mu_curve = marginal_curves["mu"]
        lambda_coordinates, lambda_curve = marginal_curves["lambda"]
        if MARGINAL_FILL:
            left.fill_betweenx(mu_coordinates, 0, mu_curve, color=MARGINAL_COLORS["mu"],
                               alpha=MARGINAL_FILL_ALPHA, linewidth=0)
        left.plot(mu_curve, mu_coordinates, color=MARGINAL_COLORS["mu"], lw=MARGINAL_LINEWIDTH, ls=MARGINAL_LINESTYLE)
        left.set(xlim=mu_plim[::-1], xlabel="Probability (%)")
        left.set_xticks(endpoint_ticks(mu_plim, nbins=3))
        left.xaxis.set_major_formatter(StrMethodFormatter(AXIS_TICK_FORMAT))
        left.xaxis.set_minor_locator(AutoMinorLocator())
        left.yaxis.tick_right()
        left.tick_params(axis="y", which="both", labelright=False, labelleft=False)
        left.spines["left"].set_visible(False)
        left.spines["right"].set_visible(True)
        if MARGINAL_FILL:
            bottom.fill_between(lambda_coordinates, 0, lambda_curve, color=MARGINAL_COLORS["lambda"],
                                alpha=MARGINAL_FILL_ALPHA, linewidth=0)
        bottom.plot(lambda_coordinates, lambda_curve, color=MARGINAL_COLORS["lambda"], lw=MARGINAL_LINEWIDTH, ls=MARGINAL_LINESTYLE)
        bottom.set(ylim=lambda_plim[::-1], ylabel="Probability (%)")
        bottom.set_yticks(endpoint_ticks(lambda_plim, nbins=3))
        bottom.yaxis.set_major_formatter(StrMethodFormatter(AXIS_TICK_FORMAT))
        bottom.yaxis.set_minor_locator(AutoMinorLocator())
        bottom.xaxis.tick_top()
        bottom.tick_params(axis="x", which="both", labeltop=False, labelbottom=False)
        bottom.yaxis.tick_right()
        bottom.yaxis.set_label_position("right")
        bottom.spines["top"].set_visible(True)
        bottom.spines["right"].set_visible(True)
        bottom.spines["bottom"].set_visible(False)
        bottom.spines["left"].set_visible(False)
        colorbar = fig.colorbar(mesh, cax=cax, orientation="vertical", extend=extend)
        colorbar.set_ticks(endpoint_ticks((norm.vmin, norm.vmax), nbins=5))
        colorbar.formatter = StrMethodFormatter(COLORBAR_TICK_FORMAT)
        colorbar.update_ticks()
        colorbar.set_label("Density", fontsize=COLORBAR_FONT_SIZE)
        cax.tick_params(labelsize=COLORBAR_FONT_SIZE)
        for letter, panel in zip("abc", (left, ax, bottom)):
            panel.set_title(f"({letter})", loc="left")
            panel.tick_params(which="minor", length=2.5, width=.7)
    return fig, {"joint": ax, "mu": left, "lambda": bottom, "colorbar": cax}

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
