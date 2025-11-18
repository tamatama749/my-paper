import os
import glob
from osgeo import gdal, ogr
import time

def merge_shapefiles(input_folder, output_file):
    """
    合并目录下所有shapefile到一个新的shapefile
    
    参数:
        input_folder: 输入文件夹路径
        output_file: 输出shapefile路径（包含.shp扩展名）
    """
    
    # 启用GDAL异常
    gdal.UseExceptions()
    
    print(f"开始处理文件夹: {input_folder}")
    
    # 查找所有shp文件
    shp_pattern = os.path.join(input_folder, "*.shp")
    shp_files = glob.glob(shp_pattern)
    
    if not shp_files:
        print("错误: 未找到任何shapefile文件！")
        return False
    
    print(f"找到 {len(shp_files)} 个shapefile文件")
    for i, f in enumerate(shp_files, 1):
        print(f"  {i}. {os.path.basename(f)}")
    
    # 如果输出文件已存在，先删除
    if os.path.exists(output_file):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        driver.DeleteDataSource(output_file)
        print(f"已删除已存在的输出文件: {output_file}")
    
    try:
        # 第一步：使用第一个文件创建输出文件
        print(f"\n步骤1: 创建输出文件（使用第一个文件）...")
        start_time = time.time()
        
        result = gdal.VectorTranslate(
            output_file,
            shp_files[0],
            format='ESRI Shapefile'
        )
        
        if result is None:
            print("错误: 创建输出文件失败！")
            return False
        
        result = None  # 释放资源
        elapsed = time.time() - start_time
        print(f"✓ 第一个文件处理完成，耗时: {elapsed:.2f}秒")
        
        # 第二步：批量追加剩余文件（如果有）
        if len(shp_files) > 1:
            print(f"\n步骤2: 追加剩余 {len(shp_files)-1} 个文件...")
            start_time = time.time()
            
            # 为了更好的内存管理，逐个文件追加
            for i, shp_file in enumerate(shp_files[1:], 2):
                print(f"  处理文件 {i}/{len(shp_files)}: {os.path.basename(shp_file)}")
                file_start = time.time()
                
                result = gdal.VectorTranslate(
                    output_file,
                    shp_file,
                    format='ESRI Shapefile',
                    accessMode='append'  # 追加模式
                )
                
                if result is None:
                    print(f"警告: 追加文件 {shp_file} 失败！")
                    continue
                
                result = None  # 释放资源
                file_elapsed = time.time() - file_start
                print(f"    ✓ 完成，耗时: {file_elapsed:.2f}秒")
            
            elapsed = time.time() - start_time
            print(f"\n✓ 所有文件追加完成，总耗时: {elapsed:.2f}秒")
        
        # 验证输出文件
        print(f"\n步骤3: 验证输出文件...")
        datasource = ogr.Open(output_file)
        if datasource is None:
            print("错误: 无法打开输出文件！")
            return False
        
        layer = datasource.GetLayer()
        feature_count = layer.GetFeatureCount()
        print(f"✓ 合并成功！")
        print(f"  输出文件: {output_file}")
        print(f"  总要素数量: {feature_count:,}")
        
        # 显示字段信息
        layer_defn = layer.GetLayerDefn()
        field_count = layer_defn.GetFieldCount()
        print(f"  字段数量: {field_count}")
        print(f"  字段列表: ", end="")
        fields = [layer_defn.GetFieldDefn(i).GetName() for i in range(field_count)]
        print(", ".join(fields))
        
        datasource = None  # 关闭文件
        
        return True
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def merge_shapefiles_geopandas(input_folder, output_file):
    """
    使用geopandas的替代方案（适用于中等数据量）
    
    参数:
        input_folder: 输入文件夹路径
        output_file: 输出shapefile路径
    """
    try:
        import geopandas as gpd
        import pandas as pd
        
        print(f"使用GeoPandas方法处理...")
        
        shp_files = glob.glob(os.path.join(input_folder, "*.shp"))
        if not shp_files:
            print("错误: 未找到任何shapefile文件！")
            return False
        
        print(f"找到 {len(shp_files)} 个文件")
        
        # 读取第一个文件以确定结构
        print("读取第一个文件...")
        gdf_list = [gpd.read_file(shp_files[0])]
        print(f"✓ 第一个文件: {len(gdf_list[0])} 个要素")
        
        # 逐个读取并追加
        for i, shp_file in enumerate(shp_files[1:], 2):
            print(f"读取文件 {i}/{len(shp_files)}: {os.path.basename(shp_file)}")
            gdf = gpd.read_file(shp_file)
            gdf_list.append(gdf)
            print(f"  ✓ {len(gdf)} 个要素")
        
        # 合并所有GeoDataFrame
        print("\n合并所有数据...")
        merged_gdf = pd.concat(gdf_list, ignore_index=True)
        
        # 保存到新文件
        print(f"保存到: {output_file}")
        merged_gdf.to_file(output_file)
        
        print(f"✓ 成功！总共 {len(merged_gdf):,} 个要素")
        
        return True
        
    except ImportError:
        print("错误: 未安装geopandas，请使用 'pip install geopandas' 安装")
        return False
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # ========== 配置参数 ==========
    # 您的实际路径
    input_folder = r"E:/CA_Fire_Analysis3/4typeEvents/new/polygon"
    output_file = r"E:/CA_Fire_Analysis3/4typeEvents/new/polygon/merge_4tpyeEvent_Poly.shp"
    
    # ========== 执行合并 ==========
    print("=" * 60)
    print("Shapefile 合并工具 - 大数据量优化版")
    print("=" * 60)
    print(f"\n输入文件夹: {input_folder}")
    print(f"输出文件: {output_file}\n")
    
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误: 输入文件夹不存在: {input_folder}")
        print("请检查路径是否正确！")
    else:
        # 方法1：使用GDAL（推荐，适合大数据量）
        success = merge_shapefiles(input_folder, output_file)
        
        # 方法2：如果GDAL不可用或失败，可以尝试GeoPandas（适合中等数据量）
        # 取消下面两行的注释来使用GeoPandas方法
        # if not success:
        #     success = merge_shapefiles_geopandas(input_folder, output_file)
        
        if success:
            print("\n" + "=" * 60)
            print("处理完成！")
            print("=" * 60)
        else:
            print("\n处理失败，请检查错误信息。")
            print("\n提示：")
            print("1. 如果提示GDAL相关错误，请尝试安装: conda install gdal")
            print("2. 可以尝试使用GeoPandas方法（取消代码中的注释）")