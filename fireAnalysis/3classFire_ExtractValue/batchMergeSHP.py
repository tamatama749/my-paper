import os
import geopandas as gpd
import pandas as pd 

# ##################################################################################################
## 批量合并逐年的同样属性FARP火斑文件# 
input_folder = r'E:/CA_Fire_Analysis/everyYrWUIburnSHP/Burn_Adj_wuiWild'      # 输入文件夹路径
output_path = r'E:/CA_Fire_Analysis/everyYrWUIburnSHP/allYr_AdWwild.shp'  # 输出文件路径（包含文件名）
print_details = True  # 是否打印详细处理信息

# 获取文件夹内所有shp文件
shp_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.shp')]
shp_files.sort()  # 排序处理文件

# 存储所有GeoDataFrame的列表
gdf_list = []

# 遍历并读取所有SHP文件
for shp in shp_files:
    try:
        # 完整文件路径
        file_path = os.path.join(input_folder, shp)
        
        # 读取GeoDataFrame
        gdf = gpd.read_file(file_path)
        
        # # 添加原始文件名作为新属性（可选）
        # gdf['source_file'] = shp
        
        # 添加到列表
        gdf_list.append(gdf)
        
        if print_details:
            print(f"成功读取文件: {shp} (要素数: {len(gdf)})")
    
    except Exception as e:
        print(f"处理 {shp} 时发生错误: {str(e)}")

# 检查是否有文件被成功读取
if not gdf_list:
    print("错误：未读取到任何有效的SHP文件")
    exit()

# 尝试合并所有GeoDataFrame
try:
    # 确保所有GeoDataFrame使用相同的坐标系
    # 以第一个文件的坐标系为准
    base_crs = gdf_list[0].crs
    gdf_list = [gdf.to_crs(base_crs) for gdf in gdf_list]
    
    # 合并所有GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True), crs=base_crs)
    
    # 保存合并后的文件
    merged_gdf.to_file(output_path, encoding='utf-8')
    
    # 输出合并信息
    print("\n=== 合并完成 ===")
    print(f"输入文件数: {len(shp_files)}")
    print(f"总要素数: {len(merged_gdf)}")
    print(f"坐标系: {base_crs}")
    print(f"输出文件: {output_path}")

except Exception as e:
    print(f"合并过程中发生错误: {str(e)}")
    

# ##################################################################################################
## 批量合并 两种WUI SHP 文件# 
# folder1 = r'E:/CA_Fire_Analysis/everyYrWUIburnSHP/interface'  # 文件夹1路径，如 r'/mnt/data/folder1'
# folder2 = r'E:/CA_Fire_Analysis/everyYrWUIburnSHP/interMix'  # 文件夹2路径，如 r'/mnt/data/folder2'
# out_folder = r'E:/CA_Fire_Analysis/everyYrWUIburnSHP/Burned_2WUI'  # 输出文件夹，如 r'/mnt/data/output_folder'
# folder1_name = os.path.basename(folder1)     # 文件夹1名字（会加入属性字段）
# folder2_name = os.path.basename(folder2)     # 文件夹2名字

# # 确保输出目录存在
# os.makedirs(out_folder, exist_ok=True)

# # 获取文件夹内所有shp文件名
# shp_files = [f for f in os.listdir(folder1) if f.lower().endswith('.shp')]
# shp_files.sort()  # 保证顺序一致

# for shp in shp_files:
#     path1 = os.path.join(folder1, shp)
#     path2 = os.path.join(folder2, shp)
    
#     # 读取shp文件
#     gdf1 = gpd.read_file(path1)
#     gdf2 = gpd.read_file(path2)
    
#     # 添加“来源”字段，记录文件夹名
#     gdf1['folder_name'] = folder1_name
#     gdf2['folder_name'] = folder2_name

#     # 统一投影（以gdf1的投影为准）
#     gdf2 = gdf2.to_crs(gdf1.crs)
    
#     # 合并
#     combined = gpd.GeoDataFrame(pd.concat([gdf1, gdf2], ignore_index=True), crs=gdf1.crs)
    
#     # 导出为新的shp文件
#     out_path = os.path.join(out_folder, shp)
#     combined.to_file(out_path, encoding='utf-8')
#     print(f'合并导出完成: {shp}')

# print('所有SHP文件合并完成！')


# ##################################################################################################
## 批量裁剪 SHP 文件（空间差集操作）

# folder_A = r'E:/CA_Fire_Analysis/Yr_farp/burnWUI'        # 文件夹A路径 (将被裁剪的SHP所在文件夹)
# folder_B = r'E:/CA_Fire_Analysis/everyYrWUIburnSHP/Burned_2WUI'        # 文件夹B路径 (用于裁剪的SHP所在文件夹)
# out_folder = r'E:/CA_Fire_Analysis/everyYrWUIburnSHP/Burn_Adj_wuiWild' # 输出文件夹路径

# # 确保输出目录存在
# os.makedirs(out_folder, exist_ok=True)

# # 获取文件夹A中所有shp文件名
# shp_files = [f for f in os.listdir(folder_A) if f.lower().endswith('.shp')]
# shp_files.sort()  # 排序保证处理顺序一致

# print(f"找到 {len(shp_files)} 个SHP文件待处理...")

# for shp in shp_files:
#     path_A = os.path.join(folder_A, shp)
#     path_B = os.path.join(folder_B, shp)
    
#     # 检查B文件夹中是否存在同名文件
#     if not os.path.exists(path_B):
#         print(f"警告: B文件夹中不存在对应文件 {shp}，跳过处理")
#         continue
    
#     # 读取shp文件
#     try:
#         gdf_A = gpd.read_file(path_A)
#         gdf_B = gpd.read_file(path_B)
        
#         # 检查数据是否为空
#         if gdf_A.empty or gdf_B.empty:
#             print(f"警告: {shp} 文件包含空数据，跳过处理")
#             continue
            
#         # 统一投影坐标系（以A的坐标系为准）
#         gdf_B = gdf_B.to_crs(gdf_A.crs)
        
#         # 执行空间差集运算 (A - B)
#         # 注：difference操作会保留A中不与B重叠的部分
#         # 选项1: , keep_geom_type=False,保留所有几何类型(包括可能产生的线和点)

#         result = gpd.overlay(gdf_A, gdf_B, how='difference', keep_geom_type=False)
#         # 选项2: , keep_geom_type=True,仅保留原始几何类型，但输出警告信息供参考
#         # print(f"  注意: {shp} 的差集运算可能丢弃了一些不同类型的几何体")
        
#         # 导出为新的shp文件
#         out_path = os.path.join(out_folder, shp)
#         result.to_file(out_path, encoding='utf-8')
#         print(f"已裁剪并导出: {shp} (保留了{len(result)}个要素)")
        
#     except Exception as e:
#         print(f"处理 {shp} 时发生错误: {str(e)}")

# print("所有SHP文件裁剪处理完成!")