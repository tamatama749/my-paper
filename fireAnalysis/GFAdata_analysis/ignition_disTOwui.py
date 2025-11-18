import geopandas as gpd
import pandas as pd
import os
from shapely.geometry import Point
import numpy as np

# 文件路径设置
ignition_path = r"E:/CA_Fire_Analysis3/GlobalFireAtlas/ignt_WUIevent/WUI_1kmbuffer_clipped_ignitions_merged.shp"
wui_folder = r"E:/data/CA_FIRE/CA_WUI/merge2WUIshp/CRS_trans"

print("开始处理火点到WUI斑块的距离计算...")

# 1. 读取起火点数据
print("正在读取火点数据...")
ignitions = gpd.read_file(ignition_path)

# 确保有dis_WUI字段，如果没有则创建（双精度型）
if 'dis_WUI' not in ignitions.columns:
    ignitions['dis_WUI'] = np.nan
    print("创建了新字段 'dis_WUI'")

# 确保dis_WUI字段是双精度型
ignitions['dis_WUI'] = ignitions['dis_WUI'].astype('float64')

# 获取所有年份
years = ignitions['YEAR_'].unique()
years = sorted([year for year in years if 2002 <= year <= 2023])
print(f"发现年份范围: {min(years)}-{max(years)}")

# 2. 按年份循环处理
for year in years:
    print(f"\n处理 {year} 年数据...")
    
    # 筛选当年火点
    year_ignitions = ignitions[ignitions['YEAR_'] == year].copy()
    if len(year_ignitions) == 0:
        print(f"  {year} 年无火点数据，跳过")
        continue
    
    print(f"  {year} 年火点数量: {len(year_ignitions)}")
    
    # 构建WUI文件路径
    wui_file = f"WUI{year}.shp"
    wui_path = os.path.join(wui_folder, wui_file)
    
    # 检查文件是否存在
    if not os.path.exists(wui_path):
        print(f"  警告: 未找到 {year} 年的WUI文件 ({wui_path})，跳过")
        continue
    
    print(f"  找到WUI文件: {os.path.basename(wui_path)}")
    
    # 读取当年WUI数据
    try:
        wui_year = gpd.read_file(wui_path)
        print(f"  WUI斑块数量: {len(wui_year)}")
        
        # 确保坐标系一致
        if wui_year.crs != ignitions.crs:
            wui_year = wui_year.to_crs(ignitions.crs)
            print(f"  WUI数据坐标系已转换为: {ignitions.crs}")
        
        # 计算最近距离
        print("  正在计算最近距离...")
        distances = []
        
        for idx, ignition_point in year_ignitions.iterrows():
            # 计算到所有WUI斑块的距离
            dists = wui_year.geometry.distance(ignition_point.geometry)
            min_distance = dists.min()
            # 保留小数点后两位
            distances.append(round(float(min_distance), 2))
        
        # 更新距离字段（确保为双精度型）
        ignitions.loc[ignitions['YEAR_'] == year, 'dis_WUI'] = np.array(distances, dtype='float64')
        
        print(f"  完成! 平均距离: {np.mean(distances):.2f} 米")
        
    except Exception as e:
        print(f"  错误: 处理 {year} 年数据时出错 - {str(e)}")
        continue

# 3. 保存结果
print("\n正在保存结果...")

# 最终确保dis_WUI字段是双精度型，并保留小数点后两位
ignitions['dis_WUI'] = ignitions['dis_WUI'].round(2).astype('float64')

# 检查字段类型
print(f"dis_WUI字段数据类型: {ignitions['dis_WUI'].dtype}")

ignitions.to_file(ignition_path)
print(f"结果已保存到: {ignition_path}")

# 输出统计信息
valid_distances = ignitions['dis_WUI'].dropna()
print(f"\n统计信息:")
print(f"成功计算距离的火点数量: {len(valid_distances)}")
print(f"总火点数量: {len(ignitions)}")
print(f"平均距离: {valid_distances.mean():.2f} 米")
print(f"最小距离: {valid_distances.min():.2f} 米")
print(f"最大距离: {valid_distances.max():.2f} 米")

print("\n处理完成!")
