# 默认图的独立精简绘图程序

本目录的 8 个 `plot_fig*.py` 分别绘制原程序的图 02–09 默认版本。每个文件都包含实际 Matplotlib 绘图代码，可直接修改字体、字号、颜色、线宽、画布和导出设置。

## 使用

1. 保持本目录 `code_s` 与旁边的 `data` 同级。
2. 在 Spyder 打开某个 `plot_fig*.py`，按 F5 显示该图。单图默认显示、不保存，与原程序一致。
3. 如需保存单图，将其顶部的 `SAVE_FIGURES` 或 `SAVE_FIGURE` 改为 `True`。
4. 运行 `run_all.py` 可一次保存全部默认图，输出位于旁边的 `output_s`，每图分别保存 PNG、PDF、SVG。

命令行也可运行：

```powershell
python run_all.py
```

各脚本支持相同调用接口：

```python
run(show=None, save=None, data_dir=None, output_dir=None)
```

依赖仅为 NumPy、Matplotlib；已验证版本列在 `requirements-tested.txt`。原图字体为 Times New Roman，复现时应保留该字体。

## 数据和默认版本

所有绘图输入均为 CSV，来自旁边 `data` 的同名图文件夹。固定默认版本的标签和样式保存在脚本中；曲线、分箱、拟合系数和概率矩阵保存在 CSV 中。程序不再读取 NPZ 或 JSON，也不使用整图 pickle 或现成图像代替绘图。

这些文件保留默认版本的最终曲线、分箱、概率网格、误差棒和缺测断线。统计/拟合结果已经固定；绘图时不再处理原始粒子、分钟分析表、原始粒径谱或雷达文件，也不读取旧绘图程序或 V1 项目。

图 08 固定为默认事件、390 m、默认质量方案、T-matrix、几何订正；图 09 固定为一分钟、默认密度关系、轴比 0.2。其他图的筛选、谱平均、分箱和拟合方式同原默认设置。

## 一致性验证

图05已按当前 selected_event_final.csv 将Case从35订正为36，脚本按CSV列名动态识别Case。图05与独立重算的订正基线、其余七图与原默认基线的300 dpi RGBA逐像素比较，差异均为0。单图独立运行和 `run_all.py` 批量运行都已检查，PNG/PDF/SVG 均成功导出，SVG 保留文字对象。原 `code` 与 V1 项目保持不变。

详细报告位于旁边 `verification_s/summary.json`；`verification_s` 仅用于核验，不是绘图依赖。

数据字段已去除来源标记，保留单位后缀，例如 `sr_mm_h`、`ze_Ka_mm6_m3`。数据按完整 float64 精度写入 CSV，除图05已要求订正的Case分组外，其余图形和数值保持不变。各表含义见旁边 data/README.md。
