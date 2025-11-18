import geopandas as gpd
import os
import pandas as pd

# 简化的测试版本，逐步检查问题
def test_shapefile_access():
    """测试shapefile文件访问"""
    
    # 可能的文件路径
    possible_paths = [
        'E:/CA_Fire_Analysis3/burnWUI/burn_2WUI_eventArea.shp',
        'E:/CA_Fire_Analysis3/burnWUI/burn_2WUI_eventArea%.shp',
        r'E:\CA_Fire_Analysis3\burnWUI\burn_2WUI_eventArea.shp',
        r'E:\CA_Fire_Analysis3\burnWUI\burn_2WUI_eventArea%.shp'
    ]
    
    print("=== 测试文件路径 ===")
    for path in possible_paths:
        print(f"检查路径: {path}")
        if os.path.exists(path):
            print(f"✓ 文件存在: {path}")
            try:
                # 尝试读取文件基本信息
                gdf = gpd.read_file(path)
                print(f"  - 要素数量: {len(gdf)}")
                print(f"  - 列名: {list(gdf.columns)}")
                print(f"  - 坐标系: {gdf.crs}")
                
                # 检查OBJECTID
                if 'OBJECTID' in gdf.columns:
                    print(f"  - OBJECTID字段存在")
                    print(f"  - OBJECTID唯一值数量: {gdf['OBJECTID'].nunique()}")
                    print(f"  - OBJECTID重复情况: {gdf['OBJECTID'].value_counts().head()}")
                else:
                    print(f"  - 警告: 未找到OBJECTID字段")
                    print(f"  - 可用字段: {list(gdf.columns)}")
                
                return path, gdf
                
            except Exception as e:
                print(f"  ✗ 读取失败: {str(e)}")
        else:
            print(f"  ✗ 文件不存在: {path}")
    
    # 检查目录是否存在
    print("\n=== 检查目录结构 ===")
    base_paths = [
        'E:/CA_Fire_Analysis3/',
        'E:/CA_Fire_Analysis3/burnWUI/',
        r'E:\CA_Fire_Analysis3',
        r'E:\CA_Fire_Analysis3\burnWUI'
    ]
    
    for base_path in base_paths:
        if os.path.exists(base_path):
            print(f"✓ 目录存在: {base_path}")
            try:
                files = os.listdir(base_path)
                shp_files = [f for f in files if f.endswith('.shp')]
                print(f"  - shapefile文件: {shp_files}")
            except Exception as e:
                print(f"  ✗ 无法列出文件: {str(e)}")
        else:
            print(f"✗ 目录不存在: {base_path}")
    
    return None, None

if __name__ == "__main__":
    try:
        valid_path, gdf = test_shapefile_access()
        
        if valid_path:
            print(f"\n=== 成功找到有效文件 ===")
            print(f"路径: {valid_path}")
        else:
            print(f"\n=== 未找到有效的shapefile文件 ===")
            print("请检查:")
            print("1. E盘是否存在")
            print("2. 文件路径是否正确")
            print("3. shapefile文件及其配套文件(.dbf, .shx, .prj)是否完整")
            
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")