import pandas as pd  
import matplotlib.pyplot as plt  

# 1. 读取数据  
# 使用Pandas库读取CSV文件  
data = pd.read_csv('E:/CA_Fire_Analysis/WUI/cityAnaly/LA.csv')  

# 2. 创建映射字典  
# 将'CAUSE'字段的值映射到四个大类  
cause_mapping = {  
    1: 'Natural', 17: 'Natural',  
    2: 'Human-Production', 5: 'Human-Production',  
    6: 'Human-Production', 10: 'Human-Production',  
    11: 'Human-Production', 12: 'Human-Production',  
    13: 'Human-Production', 15: 'Human-Production',  
    16: 'Human-Production', 18: 'Human-Production',  
    7: 'Human-Living', 8: 'Human-Living',  
    3: 'Human-Living', 4: 'Human-Living',  
    19: 'Human-Living', 14: 'Other',   
    9: 'Other'  
}  

# 3. 映射'CAUSE'列  
# 使用映射字典将数据分类  
data['CAUSE_CATEGORY'] = data['CAUSE'].map(cause_mapping)  

# 4. 创建YEAR分组  
# 定义分组边界，包括2021-2023作为一个独立标签  
year_bins = [1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023]  
year_labels = ['1980-1985', '1986-1990', '1991-1995', '1996-2000',  
               '2001-2005', '2006-2010', '2011-2015', '2016-2020', '2021-2023']  

# 创建一个新的列，用于存储分组后的年份  
data['YEAR_GROUP'] = pd.cut(data['YEAR_'], bins=year_bins, labels=year_labels, right=False)  
###################################################################################################
# # 5. 统计各组的CAUSE分类  
# # 使用groupby和size方法统计每个类别的数量  
# grouped_data = data.groupby(['YEAR_GROUP', 'CAUSE_CATEGORY']).size().unstack(fill_value=0)  

# # 6. 绘制堆积直方图  
# # 创建堆积条形图，x轴为样本数量，y轴为年份区间  
# # 定义自定义颜色  
# colors = ['#1f77b4','#DB2969', '#2ca02c', '#D89D33']  # 这里可以更改为您希望使用的颜色
# grouped_data.plot(kind='bar', stacked=True, color=colors)  

# # 设置图形的标题和坐标轴标签  
# plt.title('Stacked Histogram of Causes by Year Group')  
# plt.xlabel('Year Groups')  
# plt.ylabel('Number of Samples')  

# # 7. 显示图形  
# plt.show()  
###################################################################################################

# 5. 统计各组的CAUSE分类  
# 使用groupby和size方法统计每个类别的数量  
grouped_data = data.groupby(['YEAR_GROUP', 'CAUSE_CATEGORY']).size().unstack(fill_value=0)  

# 转换为百分比  
grouped_data_percent = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100  

# 6. 绘制百分比堆积直方图  
# 创建堆积条形图，x轴为样本数量的百分比，y轴为年份区间  
colors = ['#1f77b4','#DB2969', '#2ca02c', '#D89D33'] 
grouped_data_percent.plot(kind='bar', stacked=True, color=colors)  

# 设置图形的标题和坐标轴标签  
plt.title('Percentage Stacked Histogram of Causes by Year Group')  
plt.xlabel('Year Groups')  
plt.ylabel('Percentage of Samples(%)')  

# 7. 显示图形  
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
plt.show() 