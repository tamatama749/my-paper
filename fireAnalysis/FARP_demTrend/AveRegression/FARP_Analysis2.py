import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
# import pylustrator 
# pylustrator.start()

# merged_data = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/merged_file2.csv', encoding='Windows-1252')

# # 按年份（YEAR）分组，计算每组的火灾统计信息
# fire_stats = merged_data.groupby('YEAR').agg(
#     total_fires=('YEAR', 'size'),  # 计算该年火灾的总次数
#     avg_elevation=('MEAN', 'mean'),  # 计算该年所有火灾的平均海拔
#     avg_doy=('DOY', 'median'),  # 计算该年所有火灾的平均发生日
#     avg_longitude=('X', 'mean'),  # 计算该年所有火灾的平均经度
#     avg_latitude=('Y', 'mean')  # 计算该年所有火灾的平均纬度
# ).reset_index()

# # 输出结果
# print(fire_stats)

# fire_stats.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_statistics_by_year.csv', index=False, encoding='utf-8')
# print("SUCCESSFUL")


# 假设你的统计数据存储在 fire_stats 数据框中
# 示例数据读取（根据实际文件路径修改）
fire_stats = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/fire_statistics_by_year2.csv', encoding='utf-8')

# 创建散点图和回归曲线
plt.figure(figsize=(10, 6))

# 绘制散点图
sns.scatterplot(data=fire_stats, x='YEAR', y='avg_longitude', color='blue', label='Average longitude')

# # 绘制回归曲线——线性
# sns.regplot(data=fire_stats, x='YEAR', y='avg_latitude', scatter=False, color='red', line_kws={'label': 'Fitted Line'})
# # 计算拟合线的置信区间（误差带）
# slope, intercept, r_value, p_value, std_err = stats.linregress(fire_stats['YEAR'], fire_stats['avg_latitude'])
# # 使用拟合的回归系数计算回归线的预测值
# years = fire_stats['YEAR']
# predicted_latitude = slope * years + intercept
# # 计算回归线的标准误差
# residuals = fire_stats['avg_latitude'] - predicted_latitude
# std_dev = np.std(residuals)
# # 计算95%置信带的上下限
# confidence_interval = 1.96 * std_dev  # 1.96是95%置信区间的标准值
# # 绘制95%置信带（+/- 95% 置信区间）
# plt.fill_between(years, predicted_latitude - confidence_interval, predicted_latitude + confidence_interval,
#                  color='red', alpha=0.2, edgecolor='none')

# 三次多项式回归拟合
# 使用 numpy.polyfit 拟合三次多项式
z = np.polyfit(fire_stats['YEAR'], fire_stats['avg_longitude'], 3)
p = np.poly1d(z)
# 构造多项式方程字符串，用于显示在图例中
equation = f'{z[0]:.3e}x³ + {z[1]:.3e}x² + {z[2]:.3e}x + {z[3]:.3e}'
plt.plot(fire_stats['YEAR'], p(fire_stats['YEAR']), "r--", label=f'Trend Line: {equation}')

# 使用拟合的多项式系数计算回归线的预测值
poly_model = np.poly1d(z)
years = fire_stats['YEAR']
predicted_longitude = poly_model(years)

# 计算回归线的残差（实际值 - 预测值）
residuals = fire_stats['avg_longitude'] - predicted_longitude
std_dev = np.std(residuals)

# 计算95%置信带的上下限
confidence_interval = 1.96 * std_dev  # 1.96是95%置信区间的标准值


# 绘制95%置信带（+/- 95% 置信区间）
plt.fill_between(years, predicted_longitude - confidence_interval, predicted_longitude + confidence_interval,
                 color='red', alpha=0.1, edgecolor='none')

# 添加标签和标题
plt.title('Fire Average Longitude Over Time')
plt.xlabel('Year')
plt.ylabel('Average Longitude (degree)')
plt.legend()

# 显示图形
#% start: automatic generated code from pylustrator
plt.figure(1).ax_dict = {ax.get_label(): ax for ax in plt.figure(1).axes}
import matplotlib as mpl
plt.figure(1).axes[0].title.set(position=(0.5, 1.0), text='Fire Average Longitude Over Time', ha='center', fontsize=24.0)
#% end: automatic generated code from pylustrator
plt.show()