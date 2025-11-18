import os
import glob
import geopandas as gpd
import rasterio
from rasterio.mask import mask

# ------------------ 配置区：根据实际情况修改路径------------------
# 1. shp矢量文件文件夹路径（包含多个以年份结尾的shp文件）
shp_folder = r'E:/data/CA_FIRE/CA_WUI/merge2WUIshp/CRS_trans'
# #  转换后的shp文件夹路径（可以是新建的文件夹）
# converted_shp_folder = r'E:/data/CA_FIRE/CA_WUI/merge2WUIshp/CRS_trans'

# 2. 栅格数据文件夹（所有待逐年裁剪的tif文件都在这里）
tif_folder = r'E:/data/加州气象数据/最高气温clip'

# 3. 输出裁剪后栅格的文件夹
output_folder = r'E:/data/加州气象数据/最高气温clip/WUIclip'

# # 目标坐标系统  
# TARGET_CRS = 'EPSG:4269' 
# 确保输出文件夹存在
# os.makedirs(converted_shp_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# 初始化错误年份和成功计数器
error_years = []
successful_tifs = 0
try:
    # 获取所有shp文件
    shp_files = glob.glob(os.path.join(shp_folder, '*.shp'))
    
    # 随便找一个tif读取其投影作为参考
    example_tif = os.path.join(tif_folder, "PRISM_tmax_stable_4kmM3_2024.tif.tif")
    with rasterio.open(example_tif) as src:
        raster_crs = src.crs

    # 遍历所有shp文件
    for shp_path in shp_files:
        # 从文件名中提取年份（假设文件名最后4个字符是年份）
        try:
            year = os.path.splitext(os.path.basename(shp_path))[0][-4:]
            year = int(year)  # 转换为整数
        except (ValueError, IndexError):
            print(f"跳过文件 {shp_path}，无法提取有效年份")
            continue

        try:
            print(f'开始处理年份：{year}')
            
            # 读取矢量面shp并转换投影
            gdf = gpd.read_file(shp_path)
            
            print(f"SHP坐标系: {gdf.crs}")
            print(f"TIF坐标系: {raster_crs}")
            
            if gdf.crs != raster_crs:
                print("坐标系不一致，自动转换！")
                gdf = gdf.to_crs(raster_crs)
            else:
                print("坐标系一致，无需转换。")

            # 查找对应年份的.tif文件
            tif_pattern = os.path.join(tif_folder, f'PRISM_tmax_stable_4kmM3_{year}.tif.tif')
            
            if not os.path.exists(tif_pattern):
                print(f'缺少该年的tif文件：{tif_pattern}')
                error_years.append(year)
                continue

            # 打开并裁剪
            with rasterio.open(tif_pattern) as src:
                out_image, out_transform = mask(
                    src, gdf.geometry, crop=True, nodata=src.nodata)
                out_meta = src.meta.copy()

            # 更新输出的tif信息
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })

            # 输出
            out_fp = os.path.join(output_folder,  f'PRISM_tmax_{year}_clip.tif')
            
            with rasterio.open(out_fp, "w", **out_meta) as dest:
                dest.write(out_image)
            
            print(f'成功输出：{out_fp}')
            successful_tifs += 1

        except Exception as year_error:
            print(f'处理 {year} 年份时发生错误: {str(year_error)}')
            error_years.append(year)

except Exception as e:
    print(f'处理过程中发生严重错误: {str(e)}')

finally:
    # 打印处理总结
    print('\n' + '='*50)
    print(f'总共处理shp文件数: {len(shp_files)}')
    print(f'成功裁剪TIF数量: {successful_tifs}')
    
    if error_years:
        print(f'处理失败的年份: {error_years}')
    
    print('多要素剪裁时序栅格处理完成！')
    
    
# try:
#     # 获取所有原始shp文件
#     shp_files = glob.glob(os.path.join(shp_folder, '*.shp'))
    
#     # 首先进行坐标系统一转换
#     print("开始批量转换坐标系...")
#     converted_shp_files = []
#     for shp_path in shp_files:
#         try:
#             # 读取原始shp文件
#             gdf = gpd.read_file(shp_path)
            
#             # 打印原始坐标系
#             print(f"原始文件 {os.path.basename(shp_path)} 的坐标系: {gdf.crs}")
            
#             # 转换到目标坐标系
#             gdf_converted = gdf.to_crs(TARGET_CRS)
            
#             # 生成新的文件名
#             filename = os.path.basename(shp_path)
#             converted_shp_path = os.path.join(converted_shp_folder, filename)
            
#             # 保存转换后的文件
#             gdf_converted.to_file(converted_shp_path)
            
#             # 打印转换后的坐标系
#             print(f"转换后文件 {filename} 的坐标系: {gdf_converted.crs}")
            
#             converted_shp_files.append(converted_shp_path)
        
#         except Exception as convert_error:
#             print(f"转换 {shp_path} 时发生错误: {str(convert_error)}")
            
#     # 随便找一个tif读取其投影作为参考
#     example_tif = os.path.join(tif_folder, "PRISM_tmax_stable_4kmM3_2024.tif.tif")
#     with rasterio.open(example_tif) as src:
#         raster_crs = src.crs

#     # 遍历所有shp文件
#     for shp_path in converted_shp_files:
#         # 从文件名中提取年份（假设文件名最后4个字符是年份）
#         try:
#             year = os.path.splitext(os.path.basename(shp_path))[0][-4:]
#             year = int(year)  # 转换为整数
#         except (ValueError, IndexError):
#             print(f"跳过文件 {shp_path}，无法提取有效年份")
#             continue

#         try:
#             print(f'开始处理年份：{year}')
            
#             # 读取矢量面shp并转换投影
#             gdf = gpd.read_file(shp_path)
            
#             # print(f"SHP坐标系: {gdf.crs}")
#             # print(f"TIF坐标系: {raster_crs}")
            
#             # if gdf.crs != raster_crs:
#             #     print("坐标系不一致，自动转换！")
#             #     gdf = gdf.to_crs(raster_crs)
#             # else:
#             #     print("坐标系一致，无需转换。")

#             # 查找对应年份的.tif文件
#             tif_pattern = os.path.join(tif_folder, f'PRISM_tmax_stable_4kmM3_{year}.tif.tif')
            
#             if not os.path.exists(tif_pattern):
#                 print(f'缺少该年的tif文件：{tif_pattern}')
#                 error_years.append(year)
#                 continue

#            # 使用rioxarray读取并裁剪
#             raster = rioxarray.open_rsterxarray(tif_pattern)
            
#             # 确保shp和tif坐标系一致
#             gdf = gdf.to_crs(raster.rio.crs)
            
#             # 裁剪
#             clipped = raster.rio.clip(gdf.geometry, all_touched=True, drop=True)

#             # 更新输出的tif信息
#             out_meta.update({
#                 "driver": "GTiff",
#                 "height": out_image.shape[1],
#                 "width": out_image.shape[2],
#                 "transform": out_transform
#             })

#             # 输出
#             out_fp = os.path.join(output_folder, f'PRISM_tmax_{year}_clip.tif')
            
#             with rasterio.open(out_fp, "w", **out_meta) as dest:
#                 dest.write(out_image)
            
#             print(f'成功输出：{out_fp}')
#             successful_tifs += 1

#         except Exception as year_error:
#             print(f'处理 {year} 年份时发生错误: {str(year_error)}')
#             error_years.append(year)

# except Exception as e:
#     print(f'处理过程中发生严重错误: {str(e)}')

# finally:
#     # 打印处理总结
#     print('\n' + '='*50)
#     print(f'总共处理shp文件数: {len(shp_files)}')
#     print(f'成功裁剪TIF数量: {successful_tifs}')
    
#     if error_years:
#         print(f'处理失败的年份: {error_years}')
    
#     print('多要素剪裁时序栅格处理完成！')