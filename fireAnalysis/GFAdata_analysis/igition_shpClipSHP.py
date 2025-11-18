import geopandas as gpd
import pandas as pd
import os
from pathlib import Path

# 输入路径配置
wui_shp_path = r'E:\CA_Fire_Analysis2\depart_Events\Merge_burnPwild.shp'
ignition_dir = r'E:\CA_Fire_Analysis3\GlobalFireAtlas\ignitionP'
output_dir = r'E:\CA_Fire_Analysis3\GlobalFireAtlas\ignitionP\WILDevent'

# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)

print("正在读取WUI面要素文件...")
# 读取WUI面要素文件
wui_gdf = gpd.read_file(wui_shp_path)

# 获取所有年份
years = sorted(wui_gdf['YEAR_'].unique())
print(f"找到年份: {years}")

# 存储所有剪裁后的点要素
clipped_gdfs = []

for year in years:
    print(f"\n处理 {year} 年数据...")
    
    # 按年份筛选面要素
    year_wui = wui_gdf[wui_gdf['YEAR_'] == year]
    print(f"  {year} 年面要素数量: {len(year_wui)}")
    
    # 查找对应年份的点文件
    ignition_pattern = f"*{year}.shp"
    ignition_files = list(Path(ignition_dir).glob(ignition_pattern))
    
    if not ignition_files:
        print(f"  警告: 未找到 {year} 年的点文件 (pattern: {ignition_pattern})")
        continue
    
    for ignition_file in ignition_files:
        print(f"  处理点文件: {ignition_file.name}")
        
        try:
            # 读取点要素文件
            ignition_gdf = gpd.read_file(ignition_file)
            print(f"    原始点要素数量: {len(ignition_gdf)}")
            
            # 确保坐标参考系统一致
            if ignition_gdf.crs != year_wui.crs:
                print(f"    转换坐标系: {ignition_gdf.crs} -> {year_wui.crs}")
                ignition_gdf = ignition_gdf.to_crs(year_wui.crs)
            
            # 空间剪裁：保留在WUI面要素内的点
            clipped_points = gpd.sjoin(ignition_gdf, year_wui, how='inner', predicate='within')
            
            # 移除sjoin产生的重复列（如果有的话）
            cols_to_drop = [col for col in clipped_points.columns if col.endswith('_right')]
            if cols_to_drop:
                clipped_points = clipped_points.drop(columns=cols_to_drop)
            
            print(f"    剪裁后点要素数量: {len(clipped_points)}")
            
            if len(clipped_points) > 0:
                # 添加年份字段
                clipped_points['CLIP_YEAR'] = year
                clipped_gdfs.append(clipped_points)
                print(f"    成功添加 {len(clipped_points)} 个点要素")
            else:
                print(f"    该年份无点要素在WUI范围内")
                
        except Exception as e:
            print(f"    错误处理文件 {ignition_file.name}: {e}")

# 合并所有剪裁后的点要素
if clipped_gdfs:
    print(f"\n合并 {len(clipped_gdfs)} 个年份的剪裁结果...")
    merged_gdf = gpd.GeoDataFrame(pd.concat(clipped_gdfs, ignore_index=True))
    
    # 保存合并后的文件
    output_file = os.path.join(output_dir, 'Wild_clipped_ignitions_merged.shp')
    merged_gdf.to_file(output_file)
    
    print(f"\n处理完成!")
    print(f"总计点要素数量: {len(merged_gdf)}")
    print(f"输出文件: {output_file}")
    
    # 输出统计信息
    year_stats = merged_gdf['CLIP_YEAR'].value_counts().sort_index()
    print("\n各年份点要素统计:")
    for year, count in year_stats.items():
        print(f"  {year}: {count} 个点")
        
else:
    print("\n警告: 没有找到任何可处理的数据!")
