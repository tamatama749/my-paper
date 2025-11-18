import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from brokenaxes import brokenaxes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import seaborn as sns
import numpy as np


# import pylustrator 
# pylustrator.start()
# list(colormaps)
# # 读取火灾数据
# fire_data = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/fireP23_1.csv', encoding='Windows-1252')

# # 筛选有火源信息的事件
# fire_data = fire_data[~fire_data['CAUSE'].isin([0, np.nan])]
# incident_data_count = len(fire_data)
# print(f"过滤后剩余火灾事件: {incident_data_count}")

# # 根据提供的分类信息，创建一个字典来映射具体分类到四个大类
# cause_to_type = {
#     1: 'Natural', 17: 'Natural', 2: 'Human-Production', 5: 'Human-Production',
#     6: 'Human-Production', 10: 'Human-Production', 11: 'Human-Production',
#     12: 'Human-Production', 13: 'Human-Production', 15: 'Human-Production',
#     16: 'Human-Production', 18: 'Human-Production', 7: 'Human-Living',
#     8: 'Human-Living', 3: 'Human-Living', 4: 'Human-Living', 19: 'Human-Living',
#     14: 'Other', 9: 'Other'
# }

# # 创建新列 'CAUSE_type' 来表示分类大类
# fire_data['CAUSE_type'] = fire_data['CAUSE'].map(cause_to_type)

# # # 删除没有有效 'CAUSE_type' 的行
# fire_data = fire_data.dropna(subset=['CAUSE_type'])

# # 统计每个大类和小类的样本数量
# fire_counts = fire_data.groupby(['CAUSE_type', 'CAUSE']).size().unstack(fill_value=0)

#######################################################################################################
# #绘制堆积直方图显示每个火因类别的数量
# #绘制堆积直方图显示每个火因类别的数量

# print(fire_counts)

# cmap = ['#4169E1','#55280F','#F06900','#F88C01','#6A3F24','#7F563A','#FC9E02','#FFAF02','#C0C0C0','#946C4F','#BD9A7A','#763fa3','#c77dff','#E0E0E0','#D2B18F','#E7C7A5', '#FCDEBA','#e68653']
# # 绘制堆积横向直方图
# ax = fire_counts.plot(kind='barh', stacked=True, figsize=(14, 8), color=cmap)

# # 设置标题和标签
# plt.title('Distribution of Fire Incidents by Cause (Stacked)', fontsize=22)
# plt.xlabel('Number of Fire Incidents', fontsize=18)
# plt.ylabel('Fire Cause Categories', fontsize=18)

# # 设置x轴数字格式为三位分节法
# ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
# # 添加x轴的子刻度线
# ax.xaxis.set_minor_locator(plt.MultipleLocator(500))

# # 设置主刻度线和子刻度线的样式
# ax.tick_params(axis='x', which='major', direction='in', length=10, width=1.5)
# ax.tick_params(axis='x', which='minor', direction='in', length=5, width=1)
# # 设置网格线样式
# ax.grid(axis='x', which='major', linestyle='--', linewidth=0.8)

# # 调整x和y轴的字体大小
# plt.xticks(fontsize=18)
# plt.yticks(rotation=30, fontsize=18)

# # 添加图例，并根据给定的对应关系修改标签
# cause_legend = {
#     1.0: 'Lightning', 17.0: 'Volcanic', 2.0: 'Equipment Use', 5.0: 'Debris',
#     6.0: 'Railroad', 10.0: 'Vehicle', 11.0: 'Powerline', 12.0: 'Firefighter Training',
#     13.0: 'Non-Firefighter Training', 15.0: 'Structure', 16.0: 'Aircraft',
#     18.0: 'Escaped Prescribed Burn', 7.0: 'Arson', 8.0: 'Playing with Fire',
#     3.0: 'Smoking', 4.0: 'Campfire', 19.0: 'Illegal Alien Campfire',
#     14.0: 'Unknown / Unidentified', 9.0: 'Miscellaneous'
# }

# # 设置自定义图例标签
# handles, labels = ax.get_legend_handles_labels()

# # 替换图例标签，确保它们与提供的映射一致
# new_labels = [cause_legend[float(label.split(':')[0])] for label in labels]
# ax.legend(handles, new_labels, title="Cause Type", fontsize=14)

# # 显示图形
# plt.tight_layout()
# plt.show()
################################################################################################
# 删除没有有效 'CAUSE_type' 的行, 筛选去除大类为 'Other' 的数据
fire_data_filtered = fire_data[fire_data['CAUSE_type'] != 'Other']

# 统计每年不同火因造成的火灾次数
fire_count_by_year_and_cause = fire_data_filtered.groupby(['YEAR', 'CAUSE_type']).size().unstack(fill_value=0)

# 计算每年各火因的百分比
fire_count_percentage = fire_count_by_year_and_cause.div(fire_count_by_year_and_cause.sum(axis=1), axis=0) * 100

# 平滑处理：对每一列进行高斯平滑
fire_count_percentage_smoothed = fire_count_percentage.apply(lambda x: gaussian_filter1d(x, sigma=2), axis=0)

# 绘制图形
plt.figure(figsize=(12, 8))

# 绘制平滑后的百分比堆积图
colors = ['#DAA520', '#8B4513','#4169E1', '#F8F8FF']
ax1 = fire_count_percentage_smoothed.plot(kind='area', stacked=True, color=colors, alpha=0.6, figsize=(12, 8))


# # # 绘制一条拟合线在右侧Y轴
# # 创建右侧Y轴：火灾总次数变化（散点拟合二次回归趋势线）
# ax2 = ax1.twinx()
# 提取每年的火灾总次数
# total_fire_count_by_year = fire_count_by_year_and_cause.sum(axis=1)
# # 提取年份（x）和总火灾次数（y）
# x = total_fire_count_by_year.index
# y = total_fire_count_by_year.values
# # 使用二次回归拟合（np.polyfit）获得拟合系数
# coefficients = np.polyfit(x, y, 2)
# # 生成二次回归拟合的趋势线
# x_fit = np.linspace(x.min(), x.max(), 100)
# y_fit = coefficients[0] * x_fit**2 + coefficients[1] * x_fit + coefficients[2]
# # 绘制二次回归拟合曲线（趋势线）
# ax2.plot(x_fit, y_fit, color='red', label='Quadratic Fit', linestyle='-', linewidth=2)
# # # 添加散点图
# ax2.scatter(x, y, color='black', label='Total Fire Count', zorder=5, alpha=0.1)
# 设置标题和标签

# # # 绘制三条拟合线在右侧Y轴
# 创建右侧Y轴：火灾次数变化（每种火灾类别的次数拟合曲线）
ax2 = ax1.twinx()

# 定义每个类别的拟合线颜色
fit_colors = ['#DAA520', '#8B4513', '#4169E1']
categories = ['Human-Living', 'Human-Production', 'Natural']
fit_labels = []
# 为每个类别绘制拟合线
for i, category in enumerate(categories):
    # 提取每年该类别的火灾次数
    y = fire_count_by_year_and_cause[category]
    x = fire_count_by_year_and_cause.index

    # 使用二次回归拟合（np.polyfit）获得拟合系数
    coefficients = np.polyfit(x, y, 2)
    
    # 生成拟合的趋势线
    x_fit = np.linspace(x.min(), x.max(), 100)
    y_fit = coefficients[0] * x_fit**2 + coefficients[1] * x_fit + coefficients[2]
    # 计算R²
    y_true = y
    y_pred = coefficients[0] * x**2 + coefficients[1] * x + coefficients[2]
    ss_total = np.sum((y_true - np.mean(y_true))**2)
    ss_residual = np.sum((y_true - y_pred)**2)
    r_squared = 1 - (ss_residual / ss_total)

    # 将R²值加入图例标签
    fit_labels.append(f'{category} Trend (R² = {r_squared:.2f})')
    
    # 绘制拟合曲线
    ax2.plot(x_fit, y_fit, label=fit_labels[i], color=fit_colors[i], linestyle='-', linewidth=2)

    # 添加散点图（火灾次数）
    ax2.scatter(x, y, color=fit_colors[i], alpha=0.3)
    
# 设置标题和标签
plt.title('Changes in the proportion of fires per year by cause with quadratic trendline', fontsize=16)
ax1.set_xlabel('YEAR', fontsize=16)
ax1.set_ylabel('Percentage of fire events by cause (%)', fontsize=16)
# ax2.set_ylabel('Total Fire Counts', fontsize=12)
ax2.set_ylabel('Different Cause Fire Counts', fontsize=16)


# 设置图例
ax1.legend(bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=0,title='Fire Causes', fontsize=12)
# ax2.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0, title='Yearly total Fire Counts', fontsize=10)
ax2.legend(title='Fire Counts Trends', fontsize=10, loc='upper right')
# 显示图形
plt.tight_layout()
plt.show()
