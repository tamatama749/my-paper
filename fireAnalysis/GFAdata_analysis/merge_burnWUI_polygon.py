import geopandas as gpd
import os
import pandas as pd

def merge_polygons_by_objectid(input_path, output_path):
    """
    按OBJECTID字段合并面状要素
    
    Args:
        input_path (str): 输入shapefile路径
        output_path (str): 输出shapefile路径
    """
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    
    print(f"正在读取文件: {input_path}")
    
    try:
        # 读取 shapefile 文件，处理CRS问题
        import warnings
        
        # 先尝试正常读取
        try:
            gdf = gpd.read_file(input_path)
            crs_info = gdf.crs
        except Exception as crs_error:
            # 如果CRS有问题，忽略CRS警告并重新读取
            print(f"CRS解析警告: {str(crs_error)}")
            print("尝试忽略CRS信息重新读取...")
            
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                gdf = gpd.read_file(input_path)
                crs_info = "未知坐标系 (CRS解析失败)"
        
        print(f"成功读取 {len(gdf)} 个要素")
        
        # 显示数据基本信息
        print(f"数据列名: {list(gdf.columns)}")
        print(f"坐标系统: {crs_info}")
        
        # 检查 'OBJECTID_1' 列是否存在
        if 'OBJECTID_1' not in gdf.columns:
            raise ValueError("'OBJECTID_1' column not found in the shapefile.")
        
        # 检查OBJECTID字段的重复情况
        objectid_counts = gdf['OBJECTID_1'].value_counts()
        duplicates = objectid_counts[objectid_counts > 1]
        
        if len(duplicates) == 0:
            print("没有发现重复的OBJECTID，无需合并")
            return gdf
        
        print(f"发现 {len(duplicates)} 个重复的OBJECTID需要合并:")
        print(duplicates.head())
        
        # 对于非几何列和非OBJECTID列，定义聚合策略
        # 数值列使用求和，文本列使用第一个值
        agg_dict = {}
        for col in gdf.columns:
            if col not in ['OBJECTID_1', 'geometry']:
                if pd.api.types.is_numeric_dtype(gdf[col]):
                    agg_dict[col] = 'sum'  # 数值字段求和
                else:
                    agg_dict[col] = 'first'  # 文本字段取第一个值
        
        # 检查几何类型
        geom_types = gdf.geom_type.unique()
        print(f"几何类型: {geom_types}")
        
        # 按 'OBJECTID_1' 分组并合并要素
        print("正在执行合并操作...")
        
        if 'Point' in geom_types:
            # 对于点要素，使用dissolve会创建MultiPoint
            merged_gdf = gdf.dissolve(by='OBJECTID_1', aggfunc=agg_dict, as_index=False)
            
            # 将MultiPoint转换为Point（取第一个点）或保持MultiPoint格式
            print("检测到点要素，处理MultiPoint几何...")
            
            # 选择处理方式：
            # 方式1: 保持MultiPoint格式，但需要明确指定driver
            # 方式2: 转换为Point（取重心或第一个点）
            
            # 这里使用方式2：转换为Point（取重心）
            merged_gdf['geometry'] = merged_gdf.geometry.centroid
            
        else:
            # 对于面要素，正常处理
            merged_gdf = gdf.dissolve(by='OBJECTID_1', aggfunc=agg_dict, as_index=False)
        
        print(f"合并完成，从 {len(gdf)} 个要素合并为 {len(merged_gdf)} 个要素")
        
        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存合并后的结果为新的 shapefile
        print(f"正在保存结果到: {output_path}")
        
        # 对于点要素，确保几何类型一致
        if 'Point' in geom_types:
            # 明确指定为Point类型
            merged_gdf = merged_gdf[merged_gdf.geometry.geom_type == 'Point']
        
        merged_gdf.to_file(output_path)
        print("保存完成!")
        
        return merged_gdf
        
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

# 主程序
if __name__ == "__main__":
    # 输入文件路径 (确认的正确文件名)
    input_file = 'E:/CA_Fire_Analysis3/igition_select/wui_ig_fire.shp'
    
    # 输出文件路径
    output_file = 'E:/CA_Fire_Analysis3/igition_select/wui_ig_fire_MergeEvent.shp'
    
    try:
        # 执行合并操作
        result_gdf = merge_polygons_by_objectid(input_file, output_file)
        
        # 显示合并结果的基本统计信息
        print("\n=== 合并结果统计 ===")
        print(f"最终要素数量: {len(result_gdf)}")
        print(f"OBJECTID唯一值数量: {result_gdf['OBJECTID_1'].nunique()}")
        
    except Exception as e:
        print(f"程序执行失败: {str(e)}")
        print("请检查文件路径和数据格式")