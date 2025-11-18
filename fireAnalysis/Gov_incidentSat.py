import pandas as pd
import os, sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FuncFormatter
import pylustrator 
# 开启pylustrator 
pylustrator.start()
# 读取表格文件（例如 CSV）
# 尝试使用不同的编码读取文件（utf-8、ISO-8859-1、latin1
try:
    df = pd.read_csv('C:/Users/PC/py_project/fireAnalysis/GovIncident0724.csv', encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv('C:/Users/PC/py_project/fireAnalysis/GovIncident0724.csv', encoding='ISO-8859-1')
    except UnicodeDecodeError:
        df = pd.read_csv('C:/Users/PC/py_project/fireAnalysis/GovIncident0724.csv', encoding='latin1')
incident_count= len(df)
print(f"全部火灾事件数量: {incident_count}")

## 过滤掉 YEAR_occur 为 2024 的数据
df_filtered = df[df['YEAR_occur'] != 2024]
# 统计过滤后的数据数量
incident_data_count = len(df_filtered)

print(f"过滤2024年后剩余火灾事件: {incident_data_count}")

#  绘图：每年不同月份的火灾事件数量占当年百分比
# 统计每年不同 month_occur 数据的次数及其占比
month_counts = df_filtered.groupby(['YEAR_occur', 'month_occur']).size().unstack(fill_value=0)
month_percentage = month_counts.div(month_counts.sum(axis=1), axis=0) * 100
# 定义一个由浅到深的图例颜色映射
cmap = plt.cm.get_cmap('tab20', 12)
# 绘制直方图
fig, ax = plt.subplots(figsize=(6, 4))
month_percentage.plot(kind='bar', stacked=True, colormap=cmap, ax=ax)
ax.set_title('Percentage of Incidents by Month for Each Year')
ax.set_xlabel('Year')
ax.set_ylabel('Percentage (%)')
ax.legend(title='Month', bbox_to_anchor=(1.05, 1), loc='upper left', title_fontsize='13', fontsize='10')
plt.tight_layout()
#plt.grid(axis='y')
plt.grid(False)  # Disable grid lines completely
plt.show(block=False)


## 根据燃烧面积对事件进行分类
# 去除 acres_burned 为空值的数据
df_filtered2 = df_filtered.dropna(subset=['acres_burned']).copy()
df_filtered2 = df_filtered2[df_filtered2['acres_burned'] != 0].copy()
incident_area_null = len(df_filtered2)
print(f"过滤燃烧面积为空值剩余火灾事件: {incident_area_null}")
# 根据 acres_burned 的值进行分类
def categorize_acres(acres):
    if acres <= 100:
        return '0-100'
    elif acres <= 1000:
        return '100-1,000'
    elif acres <= 10000:
        return '1,000-10,000'
    elif acres <= 50000:
        return '10,000-50,000'
    else:
        return '>50,000'

# 新建一列存储分类标签
df_filtered2['acres_category'] = df_filtered2['acres_burned'].apply(categorize_acres).copy()
print(df_filtered2.head())
# 统计分类后的数据数量
category_counts = df_filtered2['acres_category'].value_counts()
# 统计每个标签的数据数量
total_records = len(df_filtered2)
category_summary = df_filtered2['acres_category'].value_counts().to_frame('count')
category_summary['percentage'] = (category_summary['count'] / total_records) * 100

# 输出统计结果
print(category_summary)

# 计算每年火灾事件的数量，并按 'acres_category' 分类
yearly_counts = df_filtered2.groupby(['YEAR_occur', 'acres_category']).size().unstack(fill_value=0)

# 绘制堆叠条形图
cmap2 = plt.cm.get_cmap('coolwarm', 5)
yearly_counts.plot(kind='bar', stacked=True, figsize=(6, 4), colormap=cmap2)
plt.title('Number of Fires incident by Acres_Burned Category')
plt.xlabel('Year')
plt.ylabel('Number of Fires')
plt.legend(title='Acres Burned Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', linewidth=0.5, color='gray')
plt.show(block=False)


## 统计每月燃烧总面积的在年度的占比
monthly_acres = df_filtered2.groupby(['YEAR_occur', 'month_occur'])['acres_burned'].sum().unstack(fill_value=0)
# 计算每年中不同月份的总燃烧面积占当年总面积的百分比
monthly_acres_percentage = monthly_acres.div(monthly_acres.sum(axis=1), axis=0) * 100
# 绘制百分比直方图
fig, ax = plt.subplots(figsize=(6, 4))
monthly_acres_percentage.plot(kind='bar', stacked=True, colormap=cmap, ax=ax)
ax.set_title('Percentage of Burned Area by Month for Each Year')
ax.set_xlabel('Year')
ax.set_ylabel('Percentage (%)')
ax.legend(title='Month', bbox_to_anchor=(1.05, 1), loc='upper left', title_fontsize='13', fontsize='10')
plt.tight_layout()
plt.show(block=False)

# #将每年四种 acres_category 的数据分别提取出来并绘制成四张箱型图
# categories = {'0-100':110,
#               '100-1,000':1100,
#               '1,000-10,000':12000,
#               '10,000-50,000':51000,
#               '>50,000':1100000
# }
# colors = ['skyblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightpink']
# # 设置统一的标题和子标题字体大小
# title_fontsize = 8
# subtitle_fontsize = 6
# label_fontsize = 4
# # 绘制每个类别的箱型图
# fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(6, 4))  # 2x3布局的子图
# axes = axes.flatten()  # 将子图矩阵展开为一维数组


# for ax, (category, y_max), color in zip(axes, categories.items(), colors):
#     # 过滤出当前类别的数据
#     data = df_filtered2[df_filtered2['acres_category'] == category]
#     # 绘制箱型图
#     boxplot = data.boxplot(column='acres_burned', by='YEAR_occur', ax=ax, patch_artist=True,
#                            boxprops=dict(facecolor=color, linewidth=0.5), medianprops=dict(color='black', linewidth=0.5),
#                            flierprops=dict(marker='x', color='red', alpha=0.5, markersize=2))
#     ax.set_title(f'Burn Area Category: {category}',fontsize=subtitle_fontsize)
#     ax.set_ylim(0, y_max)
#     ax.set_xlabel('Year', fontsize=subtitle_fontsize)
#     ax.set_ylabel('BA(acres)',fontsize=subtitle_fontsize)
#     ax.grid(False)
#     plt.setp(ax.get_xticklabels(), rotation=90)  # 将年份标签垂直显示
#     # 设置Y轴分段数量并用科学计数法显示大数字
#     ax.yaxis.set_major_locator(MaxNLocator(integer=True))
#     ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}' if x < 5000 else f'{x:.1e}'))
#     # 设置坐标轴刻度标签的字体大小
#     ax.tick_params(axis='both', which='major', labelsize=label_fontsize)
#      # 在箱型图上显示中位数
#     medians = data.groupby('YEAR_occur')['acres_burned'].median()
#     for i, (median, x_pos) in enumerate(zip(medians, range(1, len(medians) + 1))):
#             ax.text(x_pos, median, f'{median:.1f}', horizontalalignment='center', color='black', fontsize=4)


# # 隐藏空的第6个子图
# fig.delaxes(axes[-1])
# # 调整布局
# plt.suptitle('Burned Area by Year for Different Categories', fontsize=title_fontsize)
# plt.tight_layout(rect=[0, 0, 0.2, 0.88])
# plt.subplots_adjust(hspace=0.6, wspace=0.3)  # 调整子图与全局标题的距离
# plt.show(block=False)

# plt.show()

