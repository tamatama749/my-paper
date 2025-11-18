import os
import glob
import numpy as np
import pandas as pd
import rasterio

# ------------ 配置区域：请修改为对应的路径 ------------------------------------------------------------------------------------
# 栅格tif所在文件夹
clipped_raster_folder = r'E:/data/NLCD_USA/CA_NLCD'

# 结果输出路径
output_csv = r'E:/data/NLCD_USA/CA_NLCD/pixel_value_Satist.csv'


# # # ------------------ 数值型像元值（如AGB，温度降水气象变量）运行区--------------------------------------------------------------------------------------------
# # 自定义统计每个tif数据中所有像元值的最大值、最小值、平均值、中值、上四分位数和下四分位数的函数
# def analyze_raster_values(tif_file):
#     """分析单个栅格文件中像元值的统计指标"""
#     year = os.path.basename(tif_file).split('_')[7]  # 从文件名提取年份,('_')[7] 代表从左往右第7个被_分隔开的字段
    
#     with rasterio.open(tif_file) as src:
#         # 读取栅格数据
#         raster_data = src.read(1)  # 读取第一个波段
        
#         # 获取nodata值
#         nodata = src.nodata
        
#         # 排除nodata值
#         if nodata is not None:
#             valid_data = raster_data[raster_data != nodata]
#         else:
#             valid_data = raster_data

        
#         # 计算统计指标
#         max_value = np.max(valid_data)
#         min_value = np.min(valid_data)
#         mean_value = np.mean(valid_data)
#         median_value = np.median(valid_data)
#         q1_value = np.percentile(valid_data, 25)
#         q3_value = np.percentile(valid_data, 75)
        
        
#         return year, max_value, min_value, mean_value, median_value, q1_value, q3_value,

# # 获取所有裁剪后的栅格文件，注意修改栅格.tif名称，年份序列用*代替
# ######################################################################################################################
# pattern = os.path.join(clipped_raster_folder, '*.tif')
# ######################################################################################################################
# tif_files = sorted(glob.glob(pattern))

# if not tif_files:
#     print(f"在 {clipped_raster_folder} 中没有找到匹配的栅格文件")
#     exit()

# # 创建一个列表来存储结果
# results = []

# # 遍历所有栅格文件
# for tif_file in tif_files:
#     try:
#         year, max_value, min_value, mean_value, median_value, q1_value, q3_value = analyze_raster_values(tif_file)
        
#         # 存储当年的像元值统计
#         results.append({
#             'Year': year, 
#             'Max_Value': max_value, 
#             'Min_Value': min_value, 
#             'Mean_Value': mean_value, 
#             'Median_Value': median_value, 
#             'Q1_Value': q1_value, 
#             'Q3_Value': q3_value
    
#         })
        
#         print(f"已处理 {os.path.basename(tif_file)}")
#     except Exception as e:
#         print(f"处理 {os.path.basename(tif_file)} 时出错: {e}")

# # 将结果转换为pandas DataFrame
# df = pd.DataFrame(results)

# # 按年份排序
# df = df.sort_values('Year')
# # [END: 被替换的结果存储代码]

# # 保存为CSV
# df.to_csv(output_csv, index=False)

# # 打印预览
# print("\n数据预览：")
# print(df.head())

# print(f"\n统计结果已保存到: {output_csv}")


# ------------------ 类别型像元值（如landcover，burn serivity）运行区--------------------------------------------------------------------------------------------
# 自定义统计栅格中出现过的不同像元值个数的函数
def analyze_raster_values(tif_file):
    """分析单个栅格文件中不同像元值的数量"""
    year = os.path.basename(tif_file).split('_')[4]  # 从文件名提取年份
    
    with rasterio.open(tif_file) as src:
        # 读取栅格数据
        raster_data = src.read(1)  # 读取第一个波段
        
        # 获取nodata值
        nodata = src.nodata
        
        # 排除nodata值
        if nodata is not None:
            valid_data = raster_data[raster_data != nodata]
        else:
            valid_data = raster_data
        
        # 统计不同像元值的数量
        unique_values, counts = np.unique(valid_data, return_counts=True)
        
        return year, unique_values, counts

# 获取所有裁剪后的栅格文件，注意修改栅格.tif名称，年份序列用*代替
###############################################################################################################
pattern = os.path.join(clipped_raster_folder, '*.tif')
###############################################################################################################
tif_files = sorted(glob.glob(pattern))

if not tif_files:
    print(f"在 {clipped_raster_folder} 中没有找到匹配的栅格文件")
    exit()

# 创建一个字典来存储结果
results = {}

# 记录所有可能的像元值
all_pixel_values = set()

# 遍历所有栅格文件
for tif_file in tif_files:
    try:
        year, unique_values, counts = analyze_raster_values(tif_file)
        
        # 存储当年的像元值统计
        year_data = {int(val): int(count) for val, count in zip(unique_values, counts)}
        results[year] = year_data
        
        # 添加到所有可能的像元值集合
        all_pixel_values.update(unique_values)
        
        print(f"已处理 {os.path.basename(tif_file)}")
    except Exception as e:
        print(f"处理 {os.path.basename(tif_file)} 时出错: {e}")

# 将结果转换为pandas DataFrame
all_pixel_values = sorted(all_pixel_values)
years = sorted(results.keys())

# 创建一个空的DataFrame，colcums是列名，可以设置前缀f‘*****__{val}’,比如我这里是Burn seririty的等级，就缩写成BSlevel
#############################################################################################################################
df = pd.DataFrame(index=years, columns=[f'BSlevel_{val}' for val in all_pixel_values])
#############################################################################################################################

# 填充数据
for year in years:
    for val in all_pixel_values:
        count = results[year].get(val, 0)  # 如果该年份/没有这个值，则设为0
        df.loc[year, f'BSlevel_{val}'] = count

# 添加像元值总和列
df['Total_Pixels'] = df.sum(axis=1)

# 保存为CSV
df.to_csv(output_csv, index=True)

# 打印预览
print("\n数据预览：")
print(df.head())

print(f"\n统计结果已保存到: {output_csv}")