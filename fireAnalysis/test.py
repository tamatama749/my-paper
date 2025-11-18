import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
# import pylustrator 
# pylustrator.start()
# # # 假设你的统计数据存储在 fire_stats 数据框中
# # # 示例数据读取（根据实际文件路径修改）
fire_data = pd.read_csv('E:/CA_Fire_Analysis/deepAnaly/fireP23_1.csv', encoding='Windows-1252')

# # # 1. 检查收集类型 'C_METHOD' 列是否有空值，并删除包含空值的行
# fire_stats = fire_data.dropna(subset=['C_METHOD'])
fire_stats = fire_data[~fire_data['C_METHOD'].isin([0, 14, np.nan])]
# incident_data_count = len(fire_stats)
# print(f"过滤无记录方式的数据后剩余: {incident_data_count}")


######################################################################################################################
# 按照 'C_METHOD' 分组并计算每个分组的数量
grouped_data = fire_stats['C_METHOD'].value_counts()

Cmothod_labels = {
    1.0: 'GPS Ground',  2.0: 'GPS Air', 3.0: 'Infrared',
    4.0: 'Other Imagery', 5.0: 'Photo Interpretation', 6.0: 'Hand Drawn', 7.0: 'Mixed Collection Methods',
    8.0: 'Unknown'
}
colors = sns.color_palette("tab20c", len(grouped_data))
# 绘制直方图
plt.figure(figsize=(10, 6))
grouped_data.plot(kind='bar', color=colors)
# 获取索引并替换为自定义标签
labels = [Cmothod_labels.get(x, 'Unknown') for x in grouped_data.index]

plt.xticks(ticks=range(len(grouped_data)), labels=labels, rotation=45, fontsize=12)

plt.xlabel('Collection Methods')
plt.ylabel('Counts')
plt.title('C_METHOD histogram')
plt.show()
# ######################################################################################################################
# # 创建年代列
# fire_stats['Decade'] = (fire_stats['YEAR'] // 20) * 20
# # 按年代和 C_METHOD 分组并计算每个分组的数量
# grouped_data = fire_stats.groupby(['Decade', 'C_METHOD']).size().unstack(fill_value=0)

# # 计算每个年代中不同 C_METHOD 的比例
# proportions = grouped_data.div(grouped_data.sum(axis=1), axis=0)

# Cmothod_labels = {
#     1.0: 'GPS Ground',  2.0: 'GPS Air', 3.0: 'Infrared',
#     4.0: 'Other Imagery', 5.0: 'Photo Interpretation', 6.0: 'Hand Drawn', 7.0: 'Mixed Collection Methods',
#     8.0: 'Unknown'
# }
# # colors = ['royablue','violet','sage','gold','tomato','lightseagreen','sage','grey']
# # 绘制堆积直方图
# proportions.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='tab20c')

# # 设置自定义标签
# handles, labels = plt.gca().get_legend_handles_labels()
# labels = [Cmothod_labels.get(float(label), 'Unknown') for label in labels]
# plt.legend(handles, labels, title='Collection Methods')
# plt.xticks(rotation=45, fontsize=12)
# plt.xlabel('Decade')
# plt.ylabel('Proportion')
# plt.title('Proportion of C_METHOD by Decade')
# plt.show()
# # ######################################################################################################################
