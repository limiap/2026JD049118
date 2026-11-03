# 默认绘图的精简 CSV 数据

本目录按图 02–09 分别保存最终绘图数值，全部绘图输入均为 CSV。共 8 个文件夹、18 个 CSV 文件，666,251 字节（约 650.64 KiB）。不含原始粒子、完整分钟分析表、原始粒径谱、完整散射模型表或雷达原始文件。

来源标记已清理，单位后缀保留。例如 sr_huang_mm_h 改为 sr_mm_h，ze_Ka_mm6_m3、D0_mm、diameter_mm、probability_percent 等单位名称继续保留。均值、上下限、Ka/W、曲线和分箱编号用于区分数据含义，予以保留。

| 图文件夹 | CSV 文件 | 内容 |
|---|---|---|
| fig02_density_d0 | bins.csv；fit.csv | 39 个分箱点及样本SD、已完成拟合系数 |
| fig03_water_equivalent | series.csv | 默认个例三条最终降雪率曲线，包含块编号、孤立点标记、北京时间及rate_mm_h |
| fig04_diameter_velocity | hex.csv；hexagon.csv；curves.csv | 496 个六边形计数及几何、最终拟合和参考曲线，无逐粒子记录 |
| fig05_size_spectra | spectra.csv | 150 个粒径点，对应36条case平均谱、总体平均谱及4组SR平均谱 |
| fig06_gamma_sr_ze | edges.csv；mu_probability_percent.csv；lambda_probability_percent.csv；log10_N0_probability_percent.csv | 原三面板边界和60×60概率矩阵 |
| fig07_mu_lambda_joint_distribution | edges.csv；density.csv；marginals.csv；fit.csv | 原相对密度矩阵、边界、边缘曲线和拟合曲线 |
| fig08_time_series | plot_values.csv | 默认390 m事件的127个时窗，最终观测/模型dBZ及误差范围 |
| fig09_ze_sr_tmatrix | plot_values.csv；fits.csv | 默认一分钟版本的4,213组SR/Ka Ze/W Ze散点及最终拟合系数 |

图06的矩阵每行对应SR方向分箱、每列对应纵轴变量分箱，单位为%；edges.csv保存61个边界值。图07 density.csv每行对应Λ分箱、每列对应μ分箱，数值为0–1相对密度；边缘分布的单位为%。空网格以NaN保留，绘图时仍按原方式留白。

CSV 使用可无损回读float64的文本精度；时间保留原精度。未抽样，未重新拟合或改动默认统计。固定标签、样式和默认说明已放入对应 code_s 脚本，绘图时不需要NPZ、JSON、原code或V1。

运行旁边 code_s/run_all.py 可批量保存全部默认图到 output_s，每图包括PNG、PDF、SVG。数据和code_s保持同级即可读取。

data_manifest.csv记录各CSV的字节数和SHA256。完整验证报告位于旁边 verification_s/summary.json：图05按当前 selected_event_final.csv 订正 Case 分组，与独立重算的订正基线逐像素一致；其余七张图仍与原程序300dpi输出逐像素一致。


## 图05 Case订正

图05以 V1/snow_event/selected_event_final.csv 为准，将空白 case_id 按文件顺序前向填充，共51个事件、36个Case。旧Case33中2026-03-15和2026-03-16两个事件分别归入新Case33和34，旧Case34、35顺延为新Case35、36。

spectra.csv现有case_mean_01至case_mean_36。图05脚本按列名识别Case编号，不再固定35列。总体平均谱保持按分钟等权，四条SR分组谱、5301个有效分钟均未改变。仅拆分涉及的Case均值谱重新计算。核查报告位于 verification_s/fig05_case_correction.json。
