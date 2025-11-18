import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from numpy.polynomial.polynomial import Polynomial
# import pylustrator 
# pylustrator.start()
############################################################################################################################
# import chardet
# # 检测文件编码格式
# with open('E:/CA_Fire_Analysis/deepAnaly/fireP23_1.csv', 'rb') as f:
#     result = chardet.detect(f.read())
# print(result)  # 输出检测到的编码格式

# # 读取文件1，指定编码为ascii
# file1 = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/file3.csv', encoding='ascii')
# # 读取文件2，指定编码为GB2312
# file2 = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/merged_file.csv', encoding='utf-8')
# # 使用 merge 操作按 'OBJECTID_1' 列合并两个文件，保留仅能匹配的行
# merged_data = pd.merge(file1, file2, on='OBJECTID_1', how='outer')
# # 将合并后的数据保存为新的CSV文件
# merged_data.to_csv('E:/CA_Fire_Analysis/deepAnaly/merged_file2.csv', index=False, encoding='utf-8')
# # 输出合并后的数据
# print("合并成功")
############################################################################################################################
# import pandas as pd
# df_a = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/fireP23_1.csv', encoding='Windows-1252')

# # 加载数据：CenterCoastFoothills、Desert、NorthCoastM、SierraNevada、SouthCoastM、Valley

# df_b = pd.read_csv('E:/CA_Fire_Analysis/ecoArea/Valley.txt', sep=',')


# # 提取 B 的 'OBJECTID' 列的唯一值
# b_objectids = set(df_b['OBJECTID'])

# # 筛选 A 中 'OBJECTID' 列值在 B 的 'OBJECTID' 中的行
# filtered_a = df_a[df_a['OBJECTID'].isin(b_objectids)]

# # 保存结果到新的 CSV 文件（可选）
# filtered_a.to_csv('E:/CA_Fire_Analysis/ecoArea/Valley.csv', index=False, encoding='utf-8')

# # 打印筛选后的结果（可选）
# print("合并成功")
# # print(filtered_a)
# ############################################################################################################################

fire_data = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/fireP23_1.csv', encoding='Windows-1252')

# # 1. 根据火灾面积（AREA_m2）将每个事件划分为不同等级
bins = [0, 10000, 100000, 1000000, 10000000, float('inf')]
labels = ['class1: <10,000 m²', 'class2: 10,000-100,000 m²', 'class3: 100,000-1,000,000 m²', 
          'class4: 1,000,000-10,000,000 m²', 'class5: >10,000,000 m²']

# 创建一个新列 'FIRE_GRADE' 存储划分结果
fire_data['FIRE_GRADE'] = pd.cut(fire_data['AREA_m2'], bins=bins, labels=labels, right=False)

# 1.2. 根据 'FIRE_GRADE' 将数据框划分为5个子数据框
fire_class1 = fire_data[fire_data['FIRE_GRADE'] == 'class1: <10,000 m²']
fire_class2 = fire_data[fire_data['FIRE_GRADE'] == 'class2: 10,000-100,000 m²']
fire_class3 = fire_data[fire_data['FIRE_GRADE'] == 'class3: 100,000-1,000,000 m²']
fire_class4 = fire_data[fire_data['FIRE_GRADE'] == 'class4: 1,000,000-10,000,000 m²']
fire_class5 = fire_data[fire_data['FIRE_GRADE'] == 'class5: >10,000,000 m²']
# 
# 统计每个分组的样本数量绘制直方图
fire_grade_counts = fire_data['FIRE_GRADE'].value_counts()
plt.figure(figsize=(10, 6))
# colors = ['purple', 'blue','teal', 'mediumspringgreen', 'gold']
colors = ['gold', 'orange', 'orangered','tomato', 'red']
class_labels = ['XS', 'S', 'M', 'L', 'XL']
fire_grade_counts.plot(kind='bar', color=colors, alpha=0.7)

# 设置标题和标签
plt.title('Fire Incidents Distribution by Area', fontsize=22)
plt.xlabel('Fire Size Classes', fontsize=14)
plt.ylabel('Number of Fire Incidents', fontsize=14)
plt.xticks(ticks=range(len(fire_grade_counts)), labels=class_labels, rotation=1, fontsize=18, ha='right')

# 显示图形
plt.tight_layout()
plt.show()
# # 1.3. 将每个数据框保存为单独的CSV文件，编码为UTF-8
# fire_class1.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_class1.csv', index=False, encoding='utf-8')
# fire_class2.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_class2.csv', index=False, encoding='utf-8')
# fire_class3.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_class3.csv', index=False, encoding='utf-8')
# fire_class4.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_class4.csv', index=False, encoding='utf-8')
# fire_class5.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_class5.csv', index=False, encoding='utf-8')

# print("CSV files have been successfully saved!")
# 创建散点图和回归曲线
############################################################################################################################

plt.figure(figsize=(10, 6))

############################################################################################################################
# 2. 统计每年不同等级火灾的次数
fire_count_by_year_and_grade = fire_data.groupby(['YEAR', 'FIRE_GRADE']).size().unstack(fill_value=0)

# 计算每年各等级的百分比
fire_count_percentage = fire_count_by_year_and_grade.div(fire_count_by_year_and_grade.sum(axis=1), axis=0) * 100

# 平滑处理：对每一列进行移动平均/高斯平滑
from scipy.ndimage import gaussian_filter1d
fire_count_percentage_smoothed = fire_count_percentage.apply(lambda x: gaussian_filter1d(x, sigma=3), axis=0)
# fire_count_percentage_smoothed = fire_count_percentage.rolling(window=7, min_periods=1).mean()

# 3. 绘制平滑后的百分比堆积图和折线
plt.figure(figsize=(12, 6))

# 创建左侧Y轴：平滑后的百分比堆积图
ax1 = fire_count_percentage_smoothed.plot(kind='area', stacked=True, colormap='autumn_r', alpha=0.6, figsize=(12, 6))
# ax1 = fire_count_by_year_and_grade.plot(kind='area', stacked=True, colormap='viridis', alpha=0.6, figsize=(12, 6))

# 创建右侧Y轴：火灾总次数变化（散点拟合二次回归趋势线）
ax2 = ax1.twinx()

# 提取每年的火灾总次数
total_fire_count_by_year = fire_count_by_year_and_grade.sum(axis=1)

# 提取年份（x）和总火灾次数（y）
x = total_fire_count_by_year.index
y = total_fire_count_by_year.values

# 使用二次回归拟合（np.polyfit）获得拟合系数
coefficients = np.polyfit(x, y, 2)

# 生成二次回归拟合的趋势线
x_fit = np.linspace(x.min(), x.max(), 100)
y_fit = coefficients[0] * x_fit**2 + coefficients[1] * x_fit + coefficients[2]

# 绘制二次回归拟合曲线（趋势线）
ax2.plot(x_fit, y_fit, color='black', label='Quadratic Fit', linestyle='--', linewidth=2)

# 添加散点图
ax2.scatter(x, y, color='gray', label='Total Fire Count', zorder=5)

# 设置标题和标签
plt.title('Changes in the number of fires per year by class with quadratic trendline', fontsize=16)
ax1.set_xlabel('YEAR', fontsize=12)
# ax1.set_ylabel('Fire incidents count for the year', fontsize=12)
ax1.set_ylabel('The proportion of fire incidents of BA level', fontsize=12)

ax2.set_ylabel('Fire counts', fontsize=12)

# 设置图例
ax1.legend(bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=0, title='Fire classes', fontsize=10)
ax2.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0, title='Total number of fires', fontsize=10)

# plt.ylim(bottom=0, top=600)
# 显示图形
plt.tight_layout()
plt.show()