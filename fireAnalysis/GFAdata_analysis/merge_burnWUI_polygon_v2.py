import geopandas as gpd
import os
import pandas as pd

def merge_polygons_by_objectid_v2(input_path, output_path):
    """
    按OBJECTID字段合并面状要素 - 改进版本
    解决大数值字段的问题
    
    Args:
        input_path (str): 输入shapefile路径
        output_path (str): 输出shapefile路径
    """
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    
    print(f"正在读取文件: {input_path}")
    
    try:
        # 读取 shapefile 文件
        gdf = gpd.read_file(input_path)
        print(f"成功读取 {len(gdf)} 个要素")
        
        # 显示数据基本信息
        print(f"数据列名: {list(gdf.columns)}")
        print(f"坐标系统: {gdf.crs}")
        
        # 检查 'OBJECTID' 列是否存在
        if 'OBJECTID' not in gdf.columns:
            raise ValueError("'OBJECTID' column not found in the shapefile.")
        
        # 检查OBJECTID字段的重复情况
        objectid_counts = gdf['OBJECTID'].value_counts()
        duplicates = objectid_counts[objectid_counts > 1]
        
        if len(duplicates) == 0:
            print("没有发现重复的OBJECTID，无需合并")
            return gdf
        
        print(f"发现 {len(duplicates)} 个重复的OBJECTID需要合并:")
        print(f"总共需要合并的要素对: {duplicates.sum() - len(duplicates)} 个")
        
        # 处理可能造成数值溢出的字段
        numeric_fields_to_exclude = ['Shape_Leng', 'Shape_Area']  # 这些字段在合并后会重新计算
        
        # 对于非几何列和非OBJECTID列，定义聚合策略
        agg_dict = {}
        for col in gdf.columns:
            if col not in ['OBJECTID', 'geometry'] + numeric_fields_to_exclude:
                if pd.api.types.is_numeric_dtype(gdf[col]):
                    # 对于其他数值字段，使用求和
                    agg_dict[col] = 'sum'
                else:
                    # 文本字段取第一个值
                    agg_dict[col] = 'first'
        
        # 对于可能溢出的字段，先删除，合并后重新计算
        gdf_for_merge = gdf.drop(columns=numeric_fields_to_exclude)
        
        # 按 'OBJECTID' 分组并合并要素
        print("正在执行合并操作...")
        merged_gdf = gdf_for_merge.dissolve(by='OBJECTID', aggfunc=agg_dict, as_index=False)
        
        # 重新计算面积和周长
        print("重新计算几何属性...")
        merged_gdf['Shape_Area'] = merged_gdf.geometry.area
        merged_gdf['Shape_Leng'] = merged_gdf.geometry.length
        
        print(f"合并完成，从 {len(gdf)} 个要素合并为 {len(merged_gdf)} 个要素")
        
        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存合并后的结果为新的 shapefile
        print(f"正在保存结果到: {output_path}")
        merged_gdf.to_file(output_path)
        print("保存完成!")
        
        return merged_gdf
        
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

# 主程序
if __name__ == "__main__":
    # 输入文件路径
    input_file = 'E:/CA_Fire_Analysis3/burnWUI/burn_2WUI_eventArea.shp'
    
    # 输出文件路径 - 改进版本
    output_file = 'E:/CA_Fire_Analysis3/burnWUI/merged_burn_2WUI_eventArea_v2.shp'
    
    try:
        # 执行合并操作
        result_gdf = merge_polygons_by_objectid_v2(input_file, output_file)
        
        # 显示合并结果的基本统计信息
        print("\n=== 合并结果统计 ===")
        print(f"最终要素数量: {len(result_gdf)}")
        print(f"OBJECTID唯一值数量: {result_gdf['OBJECTID'].nunique()}")
        
        # 显示面积统计
        print(f"面积范围: {result_gdf['Shape_Area'].min():.2f} - {result_gdf['Shape_Area'].max():.2f}")
        print(f"平均面积: {result_gdf['Shape_Area'].mean():.2f}")
        
    except Exception as e:
        print(f"程序执行失败: {str(e)}")
        print("请检查文件路径和数据格式")