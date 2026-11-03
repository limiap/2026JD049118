"""保存图02–09的固定默认版本，输出到 manuscript_plot/output_s。"""
from pathlib import Path
import importlib.util
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt


def main():
    folder = Path(__file__).resolve().parent
    initial_style = mpl.rcParams.copy()
    outputs = []
    try:
        for script in sorted(folder.glob("plot_fig*.py")):
            mpl.rcParams.update(initial_style)
            spec = importlib.util.spec_from_file_location("simplified_" + script.stem, script)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            module.run(show=False, save=True)
            plt.close("all")
            outputs.append(script.name)
            print("Saved: " + script.name)
    finally:
        mpl.rcParams.update(initial_style)
    return outputs


if __name__ == "__main__":
    main()
