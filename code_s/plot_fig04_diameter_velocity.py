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
DATA_DIR = BASE / "data/fig04_diameter_velocity"
OUTPUT_DIR = BASE / "output_s/fig04_diameter_velocity"
FIGURE_NAME = "fig04_diameter_velocity"
SHOW_FIGURES = True
SAVE_FIGURES = False
FORMATS = ("png", "pdf", "svg")
DPI = 300

from textwrap import fill
from matplotlib.collections import PolyCollection
from matplotlib.colors import LogNorm
from matplotlib.transforms import AffineDeltaTransform

FONT_FAMILY = "Times New Roman"
FONT_SIZE = 10
LEGEND_FONT_SIZE = 7
FIGURE_WIDTH_MM = 183
FIGURE_HEIGHT_IN = 3.8
LEGEND_WRAP_CHARS = 70
COUNT_XLIM = (0, 15)
COUNT_YLIM = (0, 10)
COUNT_CMAP = "jet"
FIT_XLIM = (0, 10)
FIT_YLIM = (0, 4)
FIGURE_STYLE = {"axes.spines.top": False, "axes.spines.right": False,
                "pdf.fonttype": 42, "svg.fonttype": "none"}

def figure_style():
    """每次绘图读取最新字体参数，便于在 Spyder 中只重跑参数和出图单元。"""
    return {"axes.linewidth": .7, "lines.linewidth": 1.2,
            "legend.frameon": False, "savefig.dpi": 300,
            "figure.facecolor": "white", "axes.facecolor": "white", **FIGURE_STYLE,
            "font.family": [FONT_FAMILY], "font.size": FONT_SIZE,
            "axes.labelsize": FONT_SIZE + 1, "axes.titlesize": FONT_SIZE + .8,
            "xtick.labelsize": FONT_SIZE, "ytick.labelsize": FONT_SIZE,
            "legend.fontsize": LEGEND_FONT_SIZE,
            "mathtext.fontset": "custom", "mathtext.rm": FONT_FAMILY,
            "mathtext.it": f"{FONT_FAMILY}:italic", "mathtext.bf": f"{FONT_FAMILY}:bold",
            "mathtext.bfit": f"{FONT_FAMILY}:italic:bold", "mathtext.sf": FONT_FAMILY,
            "mathtext.fallback": "stix"}

def draw(arrays, settings):
    with plt.rc_context(figure_style()):
        fig = plt.figure(figsize=(FIGURE_WIDTH_MM/25.4, FIGURE_HEIGHT_IN), layout="constrained")
        grid = fig.add_gridspec(2, 2, width_ratios=[1,1], height_ratios=[1,.055])
        axa = fig.add_subplot(grid[0,0])
        axb = fig.add_subplot(grid[0,1])
        colorbar_ax = fig.add_subplot(grid[1,0])
        mesh = PolyCollection([arrays["hex_vertices"]], edgecolors="face", linewidths=None,
                              offsets=arrays["hex_centers"], offset_transform=AffineDeltaTransform(axa.transData))
        mesh.set_cmap(COUNT_CMAP)
        mesh.set_norm(LogNorm())
        mesh.set_array(arrays["hex_counts"])
        mesh.set_alpha(None)
        mesh.set_rasterized(True)
        mesh.autoscale_None()
        xmin,xmax,ymin,ymax = settings["extent"]
        axa.update_datalim(((xmin,ymin),(xmax,ymax)))
        axa._request_autoscale_view(tight=True)
        axa.add_collection(mesh, autolim=False)
        fig.colorbar(mesh, cax=colorbar_ax, orientation="horizontal", label="Particle count")
        axa.set(xlim=COUNT_XLIM, ylim=COUNT_YLIM,
                xticks=np.arange(0,15+.01,3), yticks=np.arange(COUNT_YLIM[0],COUNT_YLIM[1]+.01,2))
        axa.text(.03,.96,settings["particle_count_text"],transform=axa.transAxes,
                 ha="left",va="top",fontsize=FONT_SIZE)
        axa.set_title("(a)",loc="left")
        for i,curve in enumerate(settings["curves"]):
            x,y = arrays[f"curve_{i}"].T
            axb.plot(x,y,color=curve["color"],ls=curve["linestyle"],
                     lw=curve["linewidth"],label=curve["label"],zorder=curve["zorder"])
        axb.set(xlim=FIT_XLIM,ylim=FIT_YLIM)
        handles,labels = axb.get_legend_handles_labels()
        labels = [fill(label,width=LEGEND_WRAP_CHARS,break_long_words=False,break_on_hyphens=False) for label in labels]
        legend = axb.legend(handles,labels,loc="upper left",ncol=1,fontsize=LEGEND_FONT_SIZE,
                            handlelength=3.1,borderaxespad=.5,borderpad=0,labelspacing=.4)
        legend.get_texts()[0].set_fontsize(max(LEGEND_FONT_SIZE,7.2))
        axb.set_title("(b)",loc="left")
        for ax in (axa,axb):
            ax.set(xlabel="Diameter (mm)",ylabel=r"Terminal velocity (m s$^{-1}$)")
        fig.align_xlabels([axa,axb])
    return fig, (axa,axb)



# Fixed annotation and style of this completed figure; numerical coordinates are CSV.
CURVE_STYLES = [{'label': 'This study: $v = 0.891D^{0.261}$', 'color': 'black', 'linestyle': '-', 'linewidth': 2.4, 'zorder': 10}, {'label': 'Tao et al. (2021) low-velocity group', 'color': '#0072B2', 'linestyle': '--', 'linewidth': 1.5, 'zorder': 2}, {'label': 'Tao et al. (2021) high-velocity group', 'color': '#0072B2', 'linestyle': '-.', 'linewidth': 1.5, 'zorder': 2}, {'label': 'Xu et al. (2023)', 'color': 'g', 'linestyle': '--', 'linewidth': 1.5, 'zorder': 2}, {'label': 'Locatelli and Hobbs (1974) Densely rimed aggregates', 'color': '#D55E00', 'linestyle': '-.', 'linewidth': 1.5, 'zorder': 2}, {'label': 'Locatelli and Hobbs (1974) Unrimed aggregates', 'color': '#D55E00', 'linestyle': '-', 'linewidth': 1.5, 'zorder': 2}]
HEXBIN_EXTENT = [-1.6e-08, 16.000000016, 0.0, 10.0]
PARTICLE_COUNT_TEXT = 'n = 1,074,314 particles'

def load_data(root):
    """Read final occupied hexagons, shared geometry and finished curve coordinates."""
    def read_numeric(filename, fields):
        with (root / filename).open("r", encoding="utf-8-sig", newline="") as stream:
            return np.asarray([[float(row[field]) for field in fields]
                               for row in csv.DictReader(stream)], dtype=np.float64)
    hexagons = read_numeric("hex.csv", ("D_center_mm", "v_center_m_s", "count"))
    arrays = {"hex_centers": hexagons[:,:2], "hex_counts": hexagons[:,2],
              "hex_vertices": read_numeric("hexagon.csv", ("D_offset_mm", "v_offset_m_s"))}
    with (root / "curves.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for curve_id in range(len(CURVE_STYLES)):
        arrays[f"curve_{curve_id}"] = np.asarray([[float(row["D_mm"]),float(row["v_m_s"])]
                    for row in rows if int(row["curve_id"]) == curve_id], dtype=np.float64)
    return arrays, {"curves": CURVE_STYLES, "extent": HEXBIN_EXTENT,
                    "particle_count_text": PARTICLE_COUNT_TEXT}


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
