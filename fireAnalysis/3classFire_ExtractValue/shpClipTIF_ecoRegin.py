import os
import glob
import geopandas as gpd
import rasterio
from rasterio.mask import mask

# ------------------ 配置区：根据实际情况修改路径------------------
# 1. shp矢量文件路径
shp_path = r'E:/区划边界/CA/CA_ecoRegin_reclass.shp'

# 2. 栅格数据文件夹（所有待逐年裁剪的tif文件都在这里）
tif_folder = r'E:/data/加州气象数据/最高气温clip'

# 3. 输出裁剪后栅格的文件夹
output_folder = r'E:/data/加州气象数据/最高气温clip/EcoRegin_clip'

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 初始化错误和成功计数器
error_tifs = []
successful_tifs = 0

try:
    # 读取矢量面shp
    gdf = gpd.read_file(shp_path)
    
    # 获取所有tif文件
    # ###############################################################################################################
    tif_files = glob.glob(os.path.join(tif_folder, "PRISM_tmax_stable_4kmM3_*.tif.tif"))
    # ###############################################################################################################
     # 选择第一个tif文件作为参考投影
    reference_tif = tif_files[0]
    
    # 打开参考tif获取栅格投影
    with rasterio.open(reference_tif) as src:
        raster_crs = src.crs
    
    # 打印原始坐标系信息
    print(f"SHP原始坐标系: {gdf.crs}")
    print(f"TIF参考坐标系: {raster_crs}")
    
    # 将矢量数据转换到栅格坐标系
    if gdf.crs != raster_crs:
        print("坐标系不一致，自动转换！")
        gdf = gdf.to_crs(raster_crs)
        print(f"转换后SHP坐标系: {gdf.crs}")
    else:
        print("坐标系一致，无需转换。")
    
    # 获取所有唯一的US_L3CODE
    unique_codes = gdf['US_L3CODE'].unique()

    # 遍历所有tif文件
    for tif_path in tif_files:
        try:
            # 提取年份, split 按下划线 _ 分割文件名成多个部分，获取分割后的最后一个元素，要根据文件名适当修改
            ###############################################################################################################
            year = os.path.splitext(os.path.basename(tif_path))[0].split('_')[-1]
            print(f'开始处理年份：{year}')

            # 打开tif文件
            with rasterio.open(tif_path) as src:
                raster_crs = src.crs
                
                # 确保矢量数据与栅格数据投影一致
                if gdf.crs != raster_crs:
                    print("坐标系不一致，自动转换！")
                    gdf = gdf.to_crs(raster_crs)

                # 遍历每个US_L3CODE
                for code in unique_codes:
                    # 筛选特定US_L3CODE的要素
                    gdf_code = gdf[gdf['US_L3CODE'] == code]
                    
                    if gdf_code.empty:
                        print(f'US_L3CODE {code} 没有面要素')
                        continue

                    try:
                        # 裁剪
                        out_image, out_transform = mask(
                            src, gdf_code.geometry, crop=True, nodata=src.nodata)
                        out_meta = src.meta.copy()

                        # 更新输出的tif信息
                        out_meta.update({
                            "driver": "GTiff",
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform
                        })

                        # 输出
                        ###############################################################################################################
                        out_fp = os.path.join(output_folder, f'{code}_Tmax_{year}_clip.tif')
                        ###############################################################################################################
                        with rasterio.open(out_fp, "w", **out_meta) as dest:
                            dest.write(out_image)
                        
                        print(f'成功输出：{out_fp}')
                        successful_tifs += 1

                    except Exception as code_error:
                        print(f'处理 {code} 时发生错误: {str(code_error)}')
                        error_tifs.append(f"{code}_{year}")

        except Exception as year_error:
            print(f'处理 {tif_path} 时发生错误: {str(year_error)}')
            error_tifs.append(tif_path)

except Exception as e:
    print(f'处理过程中发生严重错误: {str(e)}')

finally:
    # 打印处理总结
    print('\n' + '='*50)
    print(f'成功裁剪TIF数量: {successful_tifs}')