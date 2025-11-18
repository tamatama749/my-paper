import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# 导入pylustrator 
import pylustrator 
# 开启pylustrator 
pylustrator.start()

# 设置字体为 SimHei 显示中文，并关闭负号显示的报错
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 加载数据
file_path = 'E:/data/华东六省/调查数据/FULEtest/deadSatistic.csv'
data = pd.read_csv(file_path, encoding='gbk')

# 重命名列，使其更具可读性
data.columns = [
    'Index', 'Plot_ID', 'Tree_ID', 'Stand_1993', 'Measurement_1993', 'Species_1993', 'DBH_1993', 'Volume_1993',
    'Stand_1998', 'Measurement_1998', 'Species_1998', 'DBH_1998', 'Volume_1998',
    'Stand_2003', 'Measurement_2003', 'Species_2003', 'DBH_2003', 'Volume_2003',
    'Stand_2008', 'Measurement_2008', 'Species_2008', 'DBH_2008', 'Volume_2008',
    'Stand_2013', 'Measurement_2013', 'Species_2013', 'DBH_2013', 'Volume_2013',
    'Stand_2018', 'Measurement_2018', 'Species_2018', 'DBH_2018', 'Volume_2018'
]

# 初始化一个空的 DataFrame 来存储统计结果
dead_tree_summary = []
# 初始化一个空的列表来存储每年枯死的树木数据
dead_tree_records = []
# 要分析的年份列表
years = [1993, 1998, 2003, 2008, 2013, 2018]

# # 分别分析每一年
# for year in years:
#     # 筛选指定年份的枯死木数据
#     dead_trees = data[(data[f'Measurement_{year}'] == '枯死木')]

#     # 按样地ID分组统计枯死木数量
#     dead_count_by_plot = dead_trees.groupby('Plot_ID').size().reset_index(name=f'Dead_Count_{year}')

#     # 统计每个样地的总树木数量
#     total_trees_by_plot = data.groupby('Plot_ID').size().reset_index(name='total_trees')
    
#     # 合并枯死木数量和总数量数据
#     plot_summary = pd.merge(total_trees_by_plot, dead_count_by_plot, on='Plot_ID', how='left').fillna(0)
    
#     # 计算枯死木占比
#     plot_summary[f'Dead_Ratio_{year}'] = plot_summary[f'Dead_Count_{year}'] / plot_summary['total_trees']
    
#     # 将年数据添加到主列表
#     dead_tree_summary.append(plot_summary[['Plot_ID', 'total_trees', f'Dead_Count_{year}', f'Dead_Ratio_{year}']])

# # 将所有年份的统计结果合并为一个 DataFrame，并删除重复的 Plot_ID 和 total_trees 列
# final_summary = pd.concat(dead_tree_summary, axis=1)
# final_summary = final_summary.loc[:, ~final_summary.columns.duplicated()]

# # 删除所有年份的枯死木数量均为 0 的样地行
# dead_count_columns = [f'Dead_Count_{year}' for year in years]
# final_summary = final_summary[final_summary[dead_count_columns].sum(axis=1) > 0]

# # 保存结果为 CSV 文件
# output_file = 'E:/data/华东六省/调查数据/FULEtest/dead_tree_statistics.csv'
# final_summary.to_csv(output_file, index=False)

# print(f"枯死木比例统计结果已保存至 {output_file}")

# 遍历每一年，提取枯死的树木信息
for year in years:
    # 筛选指定年份的枯死木数据
    dead_trees = data[data[f'Measurement_{year}'] == '枯死木']
    
    # 提取所需的列并重命名
    dead_trees_extracted = dead_trees[[
        f'Index', f'Plot_ID', f'Tree_ID', f'Species_{year}', f'DBH_{year}', f'Volume_{year}'
    ]].copy()
    
    dead_trees_extracted.columns = ['索引号','样地号','样木号', '树种', '胸径', '材积']
    dead_trees_extracted['调查枯死年份'] = year  # 添加枯死年份列
    
    # 添加当前年份的枯死木记录到列表中
    dead_tree_records.append(dead_trees_extracted)

# 将所有年份的枯死木记录合并为一个 DataFrame
final_dead_trees = pd.concat(dead_tree_records, ignore_index=True)

# 保存结果为 CSV 文件，使用utf-8-sig编码确保中文字符正确保存
output_file = 'E:/data/华东六省/调查数据/FULEtest/sample_dead_trees.csv'
final_dead_trees.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"每年枯死树木样本已保存至 {output_file}")


# 对统计筛选出的枯死木进行分析和制图
# 对统计筛选出的枯死木进行分析和制图
# 加载数据
file_path = 'E:/data/华东六省/调查数据/FULEtest/sample_dead_trees.csv'
data = pd.read_csv(file_path, encoding='gbk')
dead_tree_data = pd.DataFrame(data)
# 将树种频数较低的归为 "其他"
threshold = 20  # 设定频数阈值
species_counts = dead_tree_data['树种'].value_counts()
dead_tree_data['树种'] = dead_tree_data['树种'].apply(lambda x: x if species_counts[x] > threshold else '其他类')

# 更新频数统计
updated_counts = dead_tree_data['树种'].value_counts()

# 将调查枯死年份列转换为类别类型
dead_tree_data['调查枯死年份'] = dead_tree_data['调查枯死年份'].astype('category')
years = [1993, 1998, 2003, 2008, 2013, 2018]


# 生成每年枯死木总数，用于嵌入折线图
annual_death_counts = dead_tree_data.groupby('调查枯死年份').size().reindex(years, fill_value=0)

# 图1: 枯死木树种的频数分布图
# 绘制频数分布直方图并在顶部显示具体数值
plt.figure(figsize=(10, 6))
bars = plt.bar(updated_counts.index, updated_counts.values)
plt.title('福建省1993-2018年样地调查枯死木频数分布（小于20棵的树种合并为“其他类”）', fontsize=16)
plt.xlabel('树种', fontsize=18)
plt.ylabel('频数 (棵)', fontsize=18)
plt.xticks(rotation=45, fontsize=12)
# 在每个柱子顶部添加频数值
# 在每个 bar 顶部显示频数
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=12)
# 在右上角嵌入每年枯死木总数的折线图
dead_count_per_year = dead_tree_data['调查枯死年份'].value_counts().sort_index()
years = [1993, 1998, 2003, 2008, 2013, 2018]

# 在右上角嵌入每年枯死木总数的折线图
inset_ax = plt.gca().inset_axes([0.65, 0.65, 0.3, 0.3])  # 右上角位置
inset_ax.plot(years, annual_death_counts, marker='o', color='orange')
inset_ax.set_xticks(years)
inset_ax.set_xticklabels(years, rotation=45)  # 显示指定年份并旋转
inset_ax.set_title('每年枯死木总数', fontsize=10)
inset_ax.set_xlabel('年份', fontsize=8)
inset_ax.set_ylabel('枯死木数量', fontsize=8)
plt.show()

# # # 图2: 每年树种构成的百分比堆积图
# # species_by_year = dead_tree_data.groupby(['调查枯死年份', '树种']).size().unstack(fill_value=0)
# # species_by_year_percent = species_by_year.div(species_by_year.sum(axis=1), axis=0)

# # species_by_year_percent.plot(kind='bar', stacked=True, figsize=(10, 6))
# # plt.title('Tree Species Composition by Year (Percentage)')
# # plt.xlabel('Year')
# # plt.ylabel('Percentage')
# # plt.legend(title='树种')
# # plt.show()

# # 图3: 每年枯死木的材积箱型图

# # 提取每年枯死木的平均胸径和分位数
# mean_diameter = dead_tree_data.groupby('调查枯死年份')['胸径'].mean()
# q25_diameter = dead_tree_data.groupby('调查枯死年份')['胸径'].quantile(0.25)
# q75_diameter = dead_tree_data.groupby('调查枯死年份')['胸径'].quantile(0.75)

# # 绘制箱型图
# plt.figure(figsize=(10, 6))
# years = dead_tree_data['调查枯死年份'].unique()
# dead_tree_data.boxplot(column='胸径', by='调查枯死年份', showfliers=False, widths=0.6)
# plt.plot(range(1, len(years) + 1), mean_diameter.values, 'ro', label='平均胸径')  # 红色圆点表示平均胸径
# plt.vlines(range(1, len(years) + 1), q25_diameter.values, q75_diameter.values, colors='black', linestyles='-', lw=1, label='25%-75%分位数') 

# # 移除背景网格线
# plt.grid(False)
# # 设置横坐标的年份标签，使年份和数据对齐
# plt.xticks(ticks=range(1, len(years) + 1), labels=years, rotation=45)

# # 设置标题和标签
# plt.title('福建省枯死木胸径分布')
# plt.suptitle('')  # 移除默认标题
# plt.xlabel('调查枯死木年份')
# plt.ylabel('胸径 (cm)')
# plt.legend()  # 添加图例
# plt.show()


