import os
import glob
from osgeo import gdal, ogr, osr
import numpy as np
import time

def extract_raster_values_to_points(point_shp, raster_folder, output_shp=None):
    """
    从多个栅格文件中提取点要素位置的像元值，并保存到新字段中
    
    参数:
        point_shp: 输入点shapefile路径
        raster_folder: 栅格文件夹路径
        output_shp: 输出shapefile路径（如果为None，则直接修改输入文件）
    """
    
    # 启用GDAL异常
    gdal.UseExceptions()
    
    print("=" * 70)
    print("栅格值提取工具 - 大数据量优化版")
    print("=" * 70)
    
    # 查找所有tif文件
    tif_pattern = os.path.join(raster_folder, "*.tif")
    tif_files = glob.glob(tif_pattern)
    
    if not tif_files:
        print(f"错误: 在 {raster_folder} 中未找到任何TIF文件！")
        return False
    
    print(f"\n找到 {len(tif_files)} 个TIF文件:")
    for i, f in enumerate(tif_files, 1):
        print(f"  {i}. {os.path.basename(f)}")
    
    # 检查点shapefile是否存在
    if not os.path.exists(point_shp):
        print(f"\n错误: 点shapefile不存在: {point_shp}")
        return False
    
    # 如果没有指定输出文件，直接修改输入文件
    if output_shp is None:
        output_shp = point_shp
        print(f"\n将直接修改输入文件: {point_shp}")
    else:
        # 复制输入文件到输出文件
        print(f"\n复制shapefile到: {output_shp}")
        driver = ogr.GetDriverByName('ESRI Shapefile')
        
        # 如果输出文件已存在，删除它
        if os.path.exists(output_shp):
            driver.DeleteDataSource(output_shp)
        
        # 复制文件
        src_ds = ogr.Open(point_shp)
        driver.CopyDataSource(src_ds, output_shp)
        src_ds = None
    
    try:
        # 打开shapefile进行编辑
        vector_ds = ogr.Open(output_shp, 1)  # 1表示可写模式
        if vector_ds is None:
            print(f"错误: 无法打开shapefile进行编辑: {output_shp}")
            return False
        
        layer = vector_ds.GetLayer()
        total_features = layer.GetFeatureCount()
        print(f"\n点要素总数: {total_features:,}")
        
        # 获取图层的空间参考和范围
        layer_srs = layer.GetSpatialRef()
        extent = layer.GetExtent()
        print(f"\n点图层信息:")
        print(f"  空间参考: {layer_srs.GetName() if layer_srs else 'Unknown'}")
        print(f"  范围: X({extent[0]:.2f}, {extent[1]:.2f}), Y({extent[2]:.2f}, {extent[3]:.2f})")
        
        # 为每个tif文件创建一个新字段并提取值
        for tif_idx, tif_file in enumerate(tif_files, 1):
            print(f"\n{'='*70}")
            print(f"处理栅格 {tif_idx}/{len(tif_files)}: {os.path.basename(tif_file)}")
            print(f"{'='*70}")
            
            start_time = time.time()
            
            # 从文件名创建字段名（去掉.tif后缀）
            field_name = os.path.splitext(os.path.basename(tif_file))[0]
            
            # Shapefile字段名限制为10个字符
            if len(field_name) > 10:
                field_name = field_name[:10]
                print(f"注意: 字段名被截断为10个字符: {field_name}")
            
            # 检查字段是否已存在
            layer_defn = layer.GetLayerDefn()
            field_exists = False
            for i in range(layer_defn.GetFieldCount()):
                if layer_defn.GetFieldDefn(i).GetName() == field_name:
                    field_exists = True
                    print(f"警告: 字段 '{field_name}' 已存在，将覆盖其值")
                    break
            
            # 如果字段不存在，创建新字段
            if not field_exists:
                field_defn = ogr.FieldDefn(field_name, ogr.OFTReal)
                field_defn.SetWidth(20)
                field_defn.SetPrecision(6)
                layer.CreateField(field_defn)
                print(f"✓ 创建新字段: {field_name}")
            
            # 打开栅格文件
            raster_ds = gdal.Open(tif_file)
            if raster_ds is None:
                print(f"错误: 无法打开栅格文件: {tif_file}")
                continue
            
            # 获取栅格信息
            raster_band = raster_ds.GetRasterBand(1)
            raster_srs_wkt = raster_ds.GetProjection()
            raster_srs = osr.SpatialReference()
            raster_srs.ImportFromWkt(raster_srs_wkt)
            
            # 获取栅格的地理转换参数
            geotransform = raster_ds.GetGeoTransform()
            
            print(f"\n栅格信息:")
            print(f"  空间参考: {raster_srs.GetName() if raster_srs else 'Unknown'}")
            print(f"  尺寸: {raster_ds.RasterXSize} x {raster_ds.RasterYSize}")
            print(f"  分辨率: {geotransform[1]:.6f} x {abs(geotransform[5]):.6f}")
            
            # 计算栅格的地理范围
            minX = geotransform[0]
            maxY = geotransform[3]
            maxX = minX + geotransform[1] * raster_ds.RasterXSize
            minY = maxY + geotransform[5] * raster_ds.RasterYSize
            print(f"  范围: X({minX:.2f}, {maxX:.2f}), Y({minY:.2f}, {maxY:.2f})")
            
            # 检查是否需要坐标转换
            transform = None
            if layer_srs and raster_srs:
                if not layer_srs.IsSame(raster_srs):
                    print("\n  注意: 点和栅格的坐标系统不同，将进行坐标转换")
                    print(f"    点坐标系: {layer_srs.ExportToProj4()}")
                    print(f"    栅格坐标系: {raster_srs.ExportToProj4()}")
                    try:
                        transform = osr.CoordinateTransformation(layer_srs, raster_srs)
                        
                        # 测试转换：转换图层范围的角点
                        test_x, test_y = extent[0], extent[2]
                        test_point = ogr.Geometry(ogr.wkbPoint)
                        test_point.AddPoint(test_x, test_y)
                        test_point.Transform(transform)
                        print(f"    测试转换: ({test_x:.2f}, {test_y:.2f}) -> ({test_point.GetX():.2f}, {test_point.GetY():.2f})")
                        
                    except Exception as e:
                        print(f"    警告: 坐标转换创建失败: {e}")
                        transform = None
            
            # 获取NoData值
            nodata_value = raster_band.GetNoDataValue()
            print(f"  NoData值: {nodata_value}")
            
            # 遍历所有点要素并提取值
            layer.ResetReading()
            extracted_count = 0
            nodata_count = 0
            error_count = 0
            out_of_bounds_count = 0
            
            print(f"\n  开始提取点值...")
            progress_interval = max(1, total_features // 20)  # 显示20次进度
            
            # 用于调试：记录前几个点的详细信息
            debug_samples = 5
            debug_count = 0
            
            for feat_idx, feature in enumerate(layer):
                # 显示进度
                if feat_idx % progress_interval == 0 or feat_idx == total_features - 1:
                    progress = (feat_idx + 1) / total_features * 100
                    print(f"    进度: {progress:.1f}% ({feat_idx + 1:,}/{total_features:,})", end='\r')
                
                geom = feature.GetGeometryRef()
                if geom is None:
                    error_count += 1
                    continue
                
                # 获取点坐标
                x_orig = geom.GetX()
                y_orig = geom.GetY()
                x = x_orig
                y = y_orig
                
                # 如果需要，进行坐标转换
                if transform:
                    try:
                        point = ogr.Geometry(ogr.wkbPoint)
                        point.AddPoint(x, y)
                        point.Transform(transform)
                        x = point.GetX()
                        y = point.GetY()
                    except Exception as e:
                        if debug_count < debug_samples:
                            print(f"\n    调试 - 点{feat_idx}: 坐标转换失败: {e}")
                            debug_count += 1
                        error_count += 1
                        feature.SetField(field_name, None)
                        layer.SetFeature(feature)
                        continue
                
                # 将地理坐标转换为像素坐标
                px = int((x - geotransform[0]) / geotransform[1])
                py = int((y - geotransform[3]) / geotransform[5])
                
                # 调试信息：显示前几个点的详细转换
                if debug_count < debug_samples:
                    print(f"\n    调试 - 点{feat_idx}:")
                    print(f"      原始坐标: ({x_orig:.6f}, {y_orig:.6f})")
                    if transform:
                        print(f"      转换后: ({x:.6f}, {y:.6f})")
                    print(f"      像素坐标: ({px}, {py})")
                    print(f"      栅格尺寸: ({raster_ds.RasterXSize}, {raster_ds.RasterYSize})")
                    debug_count += 1
                
                # 检查像素坐标是否在栅格范围内
                if px < 0 or px >= raster_ds.RasterXSize or py < 0 or py >= raster_ds.RasterYSize:
                    feature.SetField(field_name, None)
                    out_of_bounds_count += 1
                else:
                    # 读取像素值
                    try:
                        pixel_value = raster_band.ReadAsArray(px, py, 1, 1)
                        if pixel_value is not None:
                            value = float(pixel_value[0, 0])
                            
                            # 检查是否为NoData
                            if nodata_value is not None and abs(value - nodata_value) < 1e-6:
                                feature.SetField(field_name, None)
                                nodata_count += 1
                            else:
                                feature.SetField(field_name, value)
                                extracted_count += 1
                        else:
                            feature.SetField(field_name, None)
                            error_count += 1
                    except Exception as e:
                        feature.SetField(field_name, None)
                        error_count += 1
                
                # 更新要素
                layer.SetFeature(feature)
            
            print()  # 换行
            
            # 关闭栅格数据集
            raster_ds = None
            
            elapsed = time.time() - start_time
            print(f"\n  ✓ 完成栅格 {tif_idx}/{len(tif_files)}")
            print(f"    - 成功提取: {extracted_count:,} 个点")
            print(f"    - NoData值: {nodata_count:,} 个点")
            print(f"    - 超出栅格范围: {out_of_bounds_count:,} 个点")
            print(f"    - 其他错误: {error_count:,} 个点")
            print(f"    - 耗时: {elapsed:.2f}秒")
        
        # 关闭矢量数据集（保存更改）
        vector_ds = None
        
        print(f"\n{'='*70}")
        print("✓ 所有栅格值提取完成！")
        print(f"输出文件: {output_shp}")
        print(f"{'='*70}")
        
        return True
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_output(shapefile_path, expected_fields):
    """
    验证输出shapefile的字段
    """
    print(f"\n验证输出文件...")
    ds = ogr.Open(shapefile_path)
    if ds is None:
        print("无法打开输出文件")
        return False
    
    layer = ds.GetLayer()
    layer_defn = layer.GetLayerDefn()
    
    print(f"\n最终字段列表:")
    for i in range(layer_defn.GetFieldCount()):
        field_name = layer_defn.GetFieldDefn(i).GetName()
        field_type = layer_defn.GetFieldDefn(i).GetTypeName()
        print(f"  {i+1}. {field_name} ({field_type})")
    
    # 显示前几个要素的样本数据
    print(f"\n前5个要素的样本数据:")
    layer.ResetReading()
    for i in range(min(5, layer.GetFeatureCount())):
        feature = layer.GetFeature(i)
        geom = feature.GetGeometryRef()
        print(f"\n要素 {i+1} - 坐标: ({geom.GetX():.6f}, {geom.GetY():.6f})")
        for field in expected_fields:
            # Shapefile字段名可能被截断
            field_short = field[:10]
            value = feature.GetField(field_short)
            print(f"  {field_short}: {value}")
    
    ds = None
    return True


if __name__ == "__main__":
    # ========== 配置参数 ==========
    point_shp = r"E:/CA_Fire_Analysis3/burnWUI/yr_Bwui_P/attribut/merge22_BwuiRegionP.shp"
    raster_folder = r"E:/data/CA_FIRE/CA_WUI/merge2WUIshp/02-23_25mRaster"
    
    # 可选：指定输出文件路径（如果不指定，将直接修改输入文件）
    # output_shp = r"E:\CA_Fire_Analysis3\burnWUI\yr_Bwui_P\attribut\merge22_BwuiRegionP_with_values.shp"
    output_shp = None  # None表示直接修改输入文件
    
    # ========== 执行提取 ==========
    print(f"\n配置信息:")
    print(f"  点shapefile: {point_shp}")
    print(f"  栅格文件夹: {raster_folder}")
    if output_shp:
        print(f"  输出文件: {output_shp}")
    else:
        print(f"  将直接修改输入文件")
    print()
    
    # 检查文件是否存在
    if not os.path.exists(point_shp):
        print(f"错误: 点shapefile不存在: {point_shp}")
    elif not os.path.exists(raster_folder):
        print(f"错误: 栅格文件夹不存在: {raster_folder}")
    else:
        # 执行提取
        success = extract_raster_values_to_points(point_shp, raster_folder, output_shp)
        
        if success:
            # 验证输出
            output_file = output_shp if output_shp else point_shp
            
            # 获取tif文件名作为预期字段
            tif_files = glob.glob(os.path.join(raster_folder, "*.tif"))
            expected_fields = [os.path.splitext(os.path.basename(f))[0][:10] for f in tif_files]
            
            verify_output(output_file, expected_fields)
            
            print("\n处理完成！")
        else:
            print("\n处理失败，请检查错误信息。")