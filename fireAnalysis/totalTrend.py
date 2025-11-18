import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from dbfread import DBF
import os, sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FuncFormatter
import seaborn as sns
# import pylustrator 
# pylustrator.start()
# 读取表格文件（例如 CSV）


# 尝试使用不同的编码读取文件（utf-8、ISO-8859-1、latin1
try:
    df = pd.read_csv('E:/CA_Fire_Analysis/FARP_23.csv', encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv('E:/CA_Fire_Analysis/FARP_23.csv', encoding='ISO-8859-1')
    except UnicodeDecodeError:
        df = pd.read_csv('E:/CA_Fire_Analysis/FARP_23.csv', encoding='latin1')
incident_count= len(df)
print(f"全部火灾事件数量: {incident_count}")

## 过滤掉 1920年前的数据
df_filtered = df[df['YEAR'] > 1920]
# 统计过滤后的数据数量
incident_data_count = len(df_filtered)

print(f"过滤1920年前剩余火灾事件: {incident_data_count}")

#Q1：发生海报是否变高？
# 计算每年的平均海拔和火灾总面积
df_grouped = df_filtered.groupby('YEAR').agg(
    avg_elevation=('DEM', 'mean'),
    total_area=('AREA_m2', 'sum'),
    fire_count=('YEAR', 'count')
).reset_index()

# 创建一个颜色渐变映射，使用火灾次数来调整颜色深浅
norm = plt.Normalize(df_grouped['fire_count'].min(), df_grouped['fire_count'].max())
cmap = sns.color_palette("Blues", as_cmap=True)

# 绘制火灾发生年份的平均海拔高度，用scatter表示圆形大小和颜色
plt.figure(figsize=(10,6))
plt.scatter(df_grouped['YEAR'], df_grouped['avg_elevation'],
            s=df_grouped['total_area'] / 10000000,  # 圆的大小与火灾总面积成比例
            c=df_grouped['fire_count'],  # 圆的颜色与火灾次数成比例
            cmap=cmap, norm=norm, alpha=0.7, edgecolor='black')

# 拟合一条线性回归线
# z = np.polyfit(df_grouped['YEAR'], df_grouped['avg_elevation'], 1)  # 一次多项式拟合（线性拟合）
z = np.polyfit(df_grouped['YEAR'], df_grouped['avg_elevation'], 3)  # 二次多项式拟合
p = np.poly1d(z)
# 构造多项式方程字符串，用于显示在图例中
equation = f'{z[0]:.3e}x³ + {z[1]:.3e}x² + {z[2]:.3e}x + {z[3]:.3e}'
plt.plot(df_grouped['YEAR'], p(df_grouped['YEAR']), "r--", label=f'Trend Line: {equation}')

# 添加颜色条
cbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap))
cbar.set_label('Fire Count')

# 添加图表标题和标签
plt.title('Average Fire Elevation by Year (After 1920)\nCircle Size by Total Area, Color by Fire Count')
plt.xlabel('Year')
plt.ylabel('Average Elevation (m)')
plt.legend()
plt.grid(True)
plt.show(block=False)

#Q2：发生时间是否提前？
## 过滤掉起火日期缺失的数据
df_filtered2 = df_filtered[df_filtered['DOY'] != 0]
# 统计过滤后的数据数量
incident_data_count2 = len(df_filtered2)
print(f"过滤起火日期不明剩余火灾事件: {incident_data_count2}")
# 计算每年的DOY中位数和众数

df_grouped = df_filtered2.groupby('YEAR').agg(
    median_doy=('DOY', 'median'),
    mode_doy=('DOY', lambda x: stats.mode(x)[0][0])  # 使用 scipy.stats 计算众数
).reset_index()

# 绘制逐年 DOY 中位数和众数的散点图
plt.figure(figsize=(10,6))
plt.scatter(df_grouped['YEAR'], df_grouped['median_doy'], color='r', label='Median DOY', s=50, marker='^', alpha=0.7)
plt.scatter(df_grouped['YEAR'], df_grouped['mode_doy'], color='none', label='Mode DOY', s=50,  edgecolors='g', marker='o',alpha=0.7)

# 为中位数拟合一条线性回归线
z_median = np.polyfit(df_grouped['YEAR'], df_grouped['median_doy'], 1)  # 一次多项式拟合
p_median = np.poly1d(z_median)
plt.plot(df_grouped['YEAR'], p_median(df_grouped['YEAR']), "r--", label='Trend Line (Median)')

# 为众数拟合一条线性回归线
z_mode = np.polyfit(df_grouped['YEAR'], df_grouped['mode_doy'], 1)  # 一次多项式拟合
p_mode = np.poly1d(z_mode)
plt.plot(df_grouped['YEAR'], p_mode(df_grouped['YEAR']), "g-", label='Trend Line (Mode)')


# 添加标题和轴标签
plt.title('Comparison of Median and Mode of DOY by Year')
plt.xlabel('Year')
plt.ylabel('DOY')
plt.legend()
plt.grid(True)
plt.show(block=False)

plt.show()
