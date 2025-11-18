import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from numpy.polynomial.polynomial import Polynomial
from scipy.stats import linregress  # 用于计算 R²
# import pylustrator 
# pylustrator.start()

# # 读取火灾数据
# fire_data = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/fireP23_1.csv', encoding='Windows-1252')

######################################################################################################################
# # 1. 删除DOY列中值为0或者空值的行
# fire_data = fire_data[~fire_data['DOY'].isin([0, np.nan])]
# incident_data_count = len(fire_data)
# print(f"过滤后剩余火灾事件: {incident_data_count}")

# # 2. 根据火灾面积（AREA_m2）将每个事件划分为不同等级
# bins = [0, 10000, 100000, 1000000, 10000000, float('inf')]
# labels = ['class1: <10,000 m²', 'class2: 10,000-100,000 m²', 'class3: 100,000-1,000,000 m²',
#           'class4: 1,000,000-10,000,000 m²', 'class5: >10,000,000 m²']

# # 创建一个新列 'FIRE_GRADE' 存储划分结果
# fire_data['FIRE_GRADE'] = pd.cut(fire_data['AREA_m2'], bins=bins, labels=labels, right=False)

# # 3. 根据 'FIRE_GRADE' 将数据框划分为5个子数据框
# fire_class1 = fire_data[fire_data['FIRE_GRADE'] == 'class1: <10,000 m²']
# fire_class2 = fire_data[fire_data['FIRE_GRADE'] == 'class2: 10,000-100,000 m²']
# fire_class3 = fire_data[fire_data['FIRE_GRADE'] == 'class3: 100,000-1,000,000 m²']
# fire_class4 = fire_data[fire_data['FIRE_GRADE'] == 'class4: 1,000,000-10,000,000 m²']
# fire_class5 = fire_data[fire_data['FIRE_GRADE'] == 'class5: >10,000,000 m²']

# # 4. 将每个数据框保存为单独的CSV文件，编码为UTF-8
# fire_class1.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass1.csv', index=False, encoding='utf-8')
# fire_class2.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass2.csv', index=False, encoding='utf-8')
# fire_class3.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass3.csv', index=False, encoding='utf-8')
# fire_class4.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass4.csv', index=False, encoding='utf-8')
# fire_class5.to_csv('E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass5.csv', index=False, encoding='utf-8')

# # 打印完成信息
# print("数据清理和划分成功，文件已保存。")
# ######################################################################################################################
# # # 筛选有火源信息的事件
# # # 1. 删除CAUSE列中值为0或者空值的行
# fire_data = fire_data[~fire_data['CAUSE'].isin([0, np.nan])]
# incident_data_count = len(fire_data)
# print(f"过滤后剩余火灾事件: {incident_data_count}")
# # 根据提供的分类信息，创建一个字典来映射具体分类到四个大类
# cause_to_type = {
#     1: 'Natural',  # Lightning-雷击
#     2: 'Human-Production',  # Equipment Use-设备使用
#     5: 'Human-Production',  # Debris-垃圾堆
#     6: 'Human-Production',  # Railroad-铁路
#     10: 'Human-Production',  # Vehicle-车辆
#     11: 'Human-Production',  # Powerline-电力线路
#     12: 'Human-Production',  # Firefighter Training- 消防员训练
#     13: 'Human-Production',  # Non-Firefighter Training-非消防员训练
#     7: 'Human-Living',  # Arson-纵火
#     8: 'Human-Living',  # Playing with Fire-玩火
#     3: 'Human-Living',  # Smoking-吸烟
#     4: 'Human-Living',  # Campfire-营火
#     14: 'Other',  # Unknown / Unidentified-未知
#     9: 'Other'  # Miscellaneous-其他原因
# }
# # 3. 创建一个新列'CAUSE_type'来表示分类大类
# fire_data['CAUSE_type'] = fire_data['CAUSE'].map(cause_to_type)

# # 4. 删除没有有效CAUSE_type的行
# fire_data = fire_data.dropna(subset=['CAUSE_type'])

# # 5. 根据'CAUSE_type'将数据分成四个子数据框
# natural_fires = fire_data[fire_data['CAUSE_type'] == 'Natural']
# other_fires = fire_data[fire_data['CAUSE_type'] == 'Other']
# human_production_fires = fire_data[fire_data['CAUSE_type'] == 'Human-Production']
# human_living_fires = fire_data[fire_data['CAUSE_type'] == 'Human-Living']

# # 6. 将每个数据框保存为单独的CSV文件
# natural_fires.to_csv('E:/CA_Fire_Analysis/deepAnaly/cause_natural.csv', index=False, encoding='utf-8')
# other_fires.to_csv('E:/CA_Fire_Analysis/deepAnaly/cause_other.csv', index=False, encoding='utf-8')
# human_production_fires.to_csv('E:/CA_Fire_Analysis/deepAnaly/cause_human_production.csv', index=False, encoding='utf-8')
# human_living_fires.to_csv('E:/CA_Fire_Analysis/deepAnaly/cause_human_living.csv', index=False, encoding='utf-8')

# # 输出完成信息
# print("数据已根据火灾原因分类并保存为4个文件。")
######################################################################################################################
# #分析不同BA等级的DOY变化
# #分析不同BA等级的DOY变化
# #分析不同BA等级的DOY变化
# #分析不同BA等级的DOY变化
# 创建一个文件路径列表
file_paths = [
    'E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass1.csv',
    'E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass2.csv',
    'E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass3.csv',
    'E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass4.csv',
    'E:/CA_Fire_Analysis/deepAnaly/fire_DOYclass5.csv'
]

# 创建一个颜色列表以区分不同的文件
#colors = ['purple', 'blue', 'teal', 'mediumspringgreen', 'gold']
colors = ['yellow','gold', '#F48C06', '#DC2F02','#9D0208']

# 创建火灾等级对应的图例标签
class_labels = ['XS', 'S', 'M', 'L', 'XL']

# 创建画布
plt.figure(figsize=(12, 8))

# 遍历所有文件路径并绘制相应的散点图和拟合曲线
for i, file_path in enumerate(file_paths):
    # 读取数据
    fire_class = pd.read_csv(file_path, encoding='utf-8')
    
    # 1. 检查DOY列是否有空值，并删除包含空值的行
    fire_class = fire_class.dropna(subset=['DOY'])
    
    # 2. 按年份（YEAR）分组，计算每组的DOY中值
    fire_stats = fire_class.groupby('YEAR')['DOY'].median().reset_index()

    # 3. 绘制DOY中值的散点图
    sns.scatterplot(data=fire_stats, x='YEAR', y='DOY', color=colors[i], label=f'Class {i+1} (scatter)', alpha=0.4)

    # 4. 线性回归拟合
    degree = 1  # 可以改为 3 来进行三次多项式拟合
    z = np.polyfit(fire_stats['YEAR'], fire_stats['DOY'], degree)  # 线性拟合
    p = np.poly1d(z)
    
    # # 5. 计算R²——线性拟合
    slope, intercept, r_value, p_value, std_err = linregress(fire_stats['YEAR'], fire_stats['DOY'])
    r_squared = r_value**2  
    #     # 5. 计算拟合值（预测值） 计算 R²——二次/三次多项式
    # y_pred = p(fire_stats['YEAR'])
    # ss_res = np.sum((fire_stats['DOY'] - y_pred) ** 2)  # 残差平方和
    # ss_tot = np.sum((fire_stats['DOY'] - np.mean(fire_stats['DOY'])) ** 2)  # 总平方和
    # r_squared = 1 - (ss_res / ss_tot)  # 计算 R²
    # 6. 绘制拟合线
    plt.plot(fire_stats['YEAR'], p(fire_stats['YEAR']), linestyle='-', color=colors[i], label=f'{class_labels[i]} (R² = {r_squared:.2f})', linewidth=2)

# 设置标题、标签和图例
plt.title('Median DOY of Fires Over Time by Fire Classes', fontsize=22)
plt.xlabel('Year', fontsize=18)
plt.ylabel('Median DOY', fontsize=18)
plt.legend(title='Fire Classes', loc='upper right')
# 设置y轴的最低值
plt.ylim(bottom=150, top=300)
# 显示图形
plt.show()
######################################################################################################################
# #分析不同火因的DOY变化
# #分析不同火因的DOY变化
# #分析不同火因的DOY变化
# # #分析不同火因的DOY变化
# file_paths = [
#     'E:/CA_Fire_Analysis/deepAnaly/cause_natural.csv',
#     'E:/CA_Fire_Analysis/deepAnaly/cause_human_production.csv',
#     'E:/CA_Fire_Analysis/deepAnaly/cause_human_living.csv',
#     'E:/CA_Fire_Analysis/deepAnaly/cause_other.csv'    
# ]

# # 创建一个颜色列表以区分不同的文件
# colors = ['#4169E1','#8B4513','#DAA520', 'gainsboro']
# # 创建火灾等级对应的图例标签
# class_labels = ['natural', 'human_production', 'human_living', 'other']
# # 创建画布
# plt.figure(figsize=(12, 8))

# # 遍历所有文件路径并绘制相应的散点图和拟合曲线
# for i, file_path in enumerate(file_paths):
#     # 读取数据
#     fire_class = pd.read_csv(file_path, encoding='utf-8')
#     # 1. 检查DOY列是否有空值，并删除包含空值的行
#     fire_class = fire_class[~fire_class['DOY'].isin([0, np.nan])]
#     incident_data_count = len(fire_class)
#     print(f"过滤后剩余火灾事件: {incident_data_count}")
#     # 2. 按年份（YEAR）分组，计算每组的DOY中值
#     fire_stats = fire_class.groupby('YEAR')['DOY'].median().reset_index()

#     # 3. 绘制DOY中值的散点图
#     sns.scatterplot(data=fire_stats, x='YEAR', y='DOY', color=colors[i], label=f'Class {i+1} (scatter)', alpha=0.4)

#     # 4. 线性回归拟合
#     degree = 2  # 可以改为 3 来进行三次多项式拟合
#     z = np.polyfit(fire_stats['YEAR'], fire_stats['DOY'], degree)  # 线性拟合
#     p = np.poly1d(z)
    
#     # # # 5. 计算R²——线性拟合
#     # slope, intercept, r_value, p_value, std_err = linregress(fire_stats['YEAR'], fire_stats['DOY'])
#     # r_squared = r_value**2  
#     #     # 5. 计算拟合值（预测值） 计算 R²——二次/三次多项式
#     y_pred = p(fire_stats['YEAR'])
#     ss_res = np.sum((fire_stats['DOY'] - y_pred) ** 2)  # 残差平方和
#     ss_tot = np.sum((fire_stats['DOY'] - np.mean(fire_stats['DOY'])) ** 2)  # 总平方和
#     r_squared = 1 - (ss_res / ss_tot)  # 计算 R²
#     # 6. 绘制拟合线
#     plt.plot(fire_stats['YEAR'], p(fire_stats['YEAR']), linestyle='-', color=colors[i], label=f'{class_labels[i]} (R² = {r_squared:.2f})', linewidth=3)

# # 设置标题、标签和图例
# plt.title('Median DOY of Fires Over Time by Fire Classes', fontsize=22)
# plt.xlabel('Year', fontsize=18)
# plt.ylabel('Median DOY', fontsize=18)
# plt.legend(title='Fire Classes', loc='upper right')
# # 设置y轴的最低值
# plt.ylim(bottom=150, top=300)
# # 显示图形
# plt.show()
######################################################################################################################
# #分析不同生态区的DOY变化
# #分析不同生态区的DOY变化
# #分析不同生态区的DOY变化

file_paths = [
    'E:/CA_Fire_Analysis/deepAnaly/ER_CenterCoastFoothills.csv',
    'E:/CA_Fire_Analysis/deepAnaly/ER_Desert.csv',
    'E:/CA_Fire_Analysis/deepAnaly/ER_NorthCoastM.csv',
    'E:/CA_Fire_Analysis/deepAnaly/ER_SierraNevada.csv',
    'E:/CA_Fire_Analysis/deepAnaly/ER_SouthCoastM.csv',
    'E:/CA_Fire_Analysis/deepAnaly/ER_Valley.csv'
]

# 创建一个颜色列表以区分不同的文件purple,blue,teal,green,gold
colors = ['gold', 'darkorange','royalblue', 'forestgreen', 'maroon', 'purple']
# 创建火灾等级对应的图例标签
class_labels = ['CenterCoastFoothills',	'Desert',	'NorthCoastM',	'SierraNevada',	'SouthCoastM', 'Valley']

# 创建画布
plt.figure(figsize=(12, 8))

# 遍历所有文件路径并绘制相应的散点图和拟合曲线
for i, file_path in enumerate(file_paths):
    # 读取数据
    fire_class = pd.read_csv(file_path, encoding='utf-8')
    # 1. 检查DOY列是否有空值，并删除包含空值的行
    fire_class = fire_class[~fire_class['DOY'].isin([0, np.nan])]
    incident_data_count = len(fire_class)
    print(f"过滤后剩余火灾事件: {incident_data_count}")
    # 2. 按年份（YEAR）分组，计算每组的DOY中值
    fire_stats = fire_class.groupby('YEAR')['DOY'].median().reset_index()

    # 3. 绘制DOY中值的散点图
    sns.scatterplot(data=fire_stats, x='YEAR', y='DOY', color=colors[i], label=f'Class {i+1} (scatter)', alpha=0.2)

    # 4. 线性回归拟合
    degree = 1  # 可以改为 3 来进行三次多项式拟合
    z = np.polyfit(fire_stats['YEAR'], fire_stats['DOY'], degree)  # 线性拟合
    p = np.poly1d(z)
    
    # # # 5. 计算R²——线性拟合
    slope, intercept, r_value, p_value, std_err = linregress(fire_stats['YEAR'], fire_stats['DOY'])
    r_squared = r_value**2  
    # #     # 5. 计算拟合值（预测值） 计算 R²——二次/三次多项式
    # y_pred = p(fire_stats['YEAR'])
    # ss_res = np.sum((fire_stats['DOY'] - y_pred) ** 2)  # 残差平方和
    # ss_tot = np.sum((fire_stats['DOY'] - np.mean(fire_stats['DOY'])) ** 2)  # 总平方和
    # r_squared = 1 - (ss_res / ss_tot)  # 计算 R²
    # 6. 绘制拟合线
    plt.plot(fire_stats['YEAR'], p(fire_stats['YEAR']), linestyle='-', color=colors[i], label=f'{class_labels[i]} (R² = {r_squared:.2f})', linewidth=3)

# 设置标题、标签和图例
plt.title('Median DOY of Fires Over Time by Eco_Regins', fontsize=22)
plt.xlabel('Year', fontsize=18)
plt.ylabel('Median DOY', fontsize=18)
plt.legend(title='Fire Classes',loc='upper right')

# 设置y轴的最低值
plt.ylim(bottom=150, top=300)
# 显示图形
plt.show()