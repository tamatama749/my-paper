import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.lines as mlines

# import pylustrator 
# pylustrator.start()
# list(colormaps)

############################################################################################################################
# #绘制每个分类的年度均值拟合线、四分位数、标准误差区间
# 读取数据
fire_class1 = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/fire_class5.csv', encoding='utf-8')

# 1. 检查海拔 'DEM' 列是否有空值，并删除包含空值的行
fire_class1 = fire_class1.dropna(subset=['DEM'])

# 2. 计算每年火灾发生的海拔平均值和总面积
yearly_stats = fire_class1.groupby('YEAR').agg(
    avg_elevation=('DEM', 'mean'), 
    total_area=('AREA_m2', 'sum'),
    lower_percentile=('DEM', lambda x: np.percentile(x, 25)),
    upper_percentile=('DEM', lambda x: np.percentile(x, 75)),
).reset_index()

# 4. 绘制散点图，使用灰度颜色表示总面积PuOr_r,bwr,BrBG_r,PiYG_r,hot
plt.figure(figsize=(12, 8))
scatter = plt.scatter(yearly_stats['YEAR'], yearly_stats['avg_elevation'], 
                      s=100, c=yearly_stats['total_area'], cmap='hot', edgecolors='gray', alpha=0.7)

# 5. 添加25%和75%分位数，表示为竖线
plt.vlines(yearly_stats['YEAR'], yearly_stats['lower_percentile'], yearly_stats['upper_percentile'], 
           colors='gray', linewidth=1, label='25th-75th Percentile Range')

# 7. 绘制三次多项式回归曲线及95%置信带
# 三次多项式拟合
z = np.polyfit(yearly_stats['YEAR'], yearly_stats['avg_elevation'], 3)
p = np.poly1d(z)
# 生成拟合曲线
x_line = np.linspace(yearly_stats['YEAR'].min(), yearly_stats['YEAR'].max(), 500)
y_line = p(x_line)

# 计算置信带
y_err = 1.96 * np.std(yearly_stats['avg_elevation'])  # 假设标准误差为样本标准差，乘以1.96获得95%置信区间
plt.fill_between(x_line, y_line - y_err, y_line + y_err, color='gold', alpha=0.1, edgecolor='none', label="95% Confidence Interval")

# 绘制回归曲线purple,blue,teal,green,gold
plt.plot(x_line, y_line, color='gold', linewidth=2, linestyle='--', label='Cubic Polynomial Fit')

# 显示多项式回归方程
equation_text = f"y = {z[0]:.4e}x³ + {z[1]:.4e}x² + {z[2]:.4e}x + {z[3]:.4e}"
# plt.text(0.5, 0.9, equation_text, ha='center', va='center', transform=plt.gca().transAxes, fontsize=12, color='red')

# 8. 添加标签和图例
plt.xlabel('Year',size=20)
plt.ylabel('Average Elevation (m)', size=20)
plt.title('XL-Fire Elevation Trends (1,000,000-10,000,000 m²)',size=24)
plt.legend()

# 10. 添加颜色条图例并显示数字格式
cbar = plt.colorbar(scatter, label='Total Burned Area of the Year (m²)', shrink=0.5, pad=0.02)
cbar.set_ticks([yearly_stats['total_area'].min(), yearly_stats['total_area'].max()])
cbar.set_ticklabels([f"{int(yearly_stats['total_area'].min()):,}", f"{int(yearly_stats['total_area'].max()):,}"])
cbar.ax.tick_params(labelsize=16)
cbar.set_label('Total Burned Area of the Year (m²)', fontsize=16)
# 11. 设置y轴的最低值为0
plt.ylim(bottom=0,top=2000)
plt.show(block=False)
plt.show()
# ############################################################################################################################
# #####11. 绘制五个拟合线在一个面板上的图
# # # 创建一个文件路径列表
# file_paths = [
#     'E:/CA_Fire_Analysis/deepAnaly/fire_class1.csv',
#     'E:/CA_Fire_Analysis/deepAnaly/fire_class2.csv',
#     'E:/CA_Fire_Analysis/deepAnaly/fire_class3.csv',
#     'E:/CA_Fire_Analysis/deepAnaly/fire_class4.csv',
#     'E:/CA_Fire_Analysis/deepAnaly/fire_class5.csv'
# ]

# # 创建一个颜色列表以区分不同的文件purple,blue,teal,green,gold
# # colors = ['purple', 'blue','teal', 'mediumspringgreen', 'gold']
# colors = ['yellow','gold', '#F48C06', '#DC2F02','#9D0208']
# # 创建火灾等级对应的图例标签
# class_labels = ['XS', 'S', 'M', 'L', 'XL']
					

# # file_paths = [
# #     'E:/CA_Fire_Analysis/deepAnaly/ER_CenterCoastFoothills.csv',
# #     'E:/CA_Fire_Analysis/deepAnaly/ER_Desert.csv',
# #     'E:/CA_Fire_Analysis/deepAnaly/ER_NorthCoastM.csv',
# #     'E:/CA_Fire_Analysis/deepAnaly/ER_SierraNevada.csv',
# #     'E:/CA_Fire_Analysis/deepAnaly/ER_SouthCoastM.csv',
# #     'E:/CA_Fire_Analysis/deepAnaly/ER_Valley.csv'
# # ]

# # # 创建一个颜色列表以区分不同的文件purple,blue,teal,green,gold
# # colors = ['gold', 'darkorange','royalblue', 'forestgreen', 'maroon', 'purple']
# # # 创建火灾等级对应的图例标签
# # class_labels = ['CenterCoastFoothills',	'Desert',	'NorthCoastM',	'SierraNevada',	'SouthCoastM', 'Valley']


# # 创建画布
# plt.figure(figsize=(12, 8))

# # 遍历所有文件路径并绘制相应的散点图和拟合曲线
# for i, file_path in enumerate(file_paths):
#     # 读取数据
#     fire_class = pd.read_csv(file_path, encoding='utf-8')
    
#     # 1. 检查海拔 'DEM' 列是否有空值，并删除包含空值的行
#     fire_stats = fire_class.dropna(subset=['DEM'])
    
#     # 按年份（YEAR）分组，计算每组的火灾统计信息
#     fire_stats = fire_stats.groupby('YEAR').agg(
#         total_fires=('YEAR', 'size'),  # 计算该年火灾的总次数
#         avg_elevation=('MEAN', 'mean')  # 计算该年所有火灾的平均海拔
#     ).reset_index()
    
#     # 绘制散点图
#     sns.scatterplot(data=fire_stats, x='YEAR', y='avg_elevation', color=colors[i], label=f'Class {i+1} (scatter)', alpha=0.3)
    
#     # 三次多项式回归拟合
#     z = np.polyfit(fire_stats['YEAR'], fire_stats['avg_elevation'], 3)
#     p = np.poly1d(z)
    
#     # 计算拟合值（预测值）用于算R2
#     y_pred = p(fire_stats['YEAR'])
#     ss_res = np.sum((fire_stats['avg_elevation'] - y_pred) ** 2)  # 残差平方和
#     ss_tot = np.sum((fire_stats['avg_elevation'] - np.mean(fire_stats['avg_elevation'])) ** 2)  # 总平方和
#     r_squared = 1 - (ss_res / ss_tot)  # 计算 R²    
#     # 绘制拟合曲线
#     plt.plot(fire_stats['YEAR'], p(fire_stats['YEAR']), linestyle='-', color=colors[i], label=f'{class_labels[i]} (R² = {r_squared:.2f})', linewidth=2)

# # 设置标题、标签和图例
# plt.title('Fire Average Elevation Over Time by 5 Class', fontsize=22)
# plt.xlabel('Year', fontsize=18)
# plt.ylabel('Average Elevation (m)', fontsize=18)
# plt.legend(title='Fire Classes',loc='upper right')
# # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0,numpoints=1,title='Fire Classes')
# # plt.show(block=False)

# # 显示图形
# plt.show()
# plt.ion()