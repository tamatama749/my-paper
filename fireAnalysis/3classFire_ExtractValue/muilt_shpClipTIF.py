import os
import glob
import geopandas as gpd
import rasterio
from rasterio.mask import mask

# ------------------ 配置区：根据实际情况修改路径------------------
# 1. shp矢量文件路径
shp_path = r'E:/CA_Fire_Analysis/everyYrWUIburnSHP/allYr_M_2WUI.shp'

# 2. 栅格数据文件夹（所有待逐年裁剪的tif文件都在这里）
tif_folder = r'E:/CA-Biomass/CECS/CStocks_Live202211'

# 3. 输出裁剪后栅格的文件夹
output_folder = r'E:/CA_Fire_Analysis2/codetest'

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 初始化错误年份和成功计数器
error_years = []
successful_tifs = 0

try:
    # 读取矢量面shp并和栅格文件统一投影
    gdf = gpd.read_file(shp_path)
    # ###############################################################################################################
    # 随便找一年tif读取其投影
    example_tif = os.path.join(tif_folder, "CStocks_Live_1985.tif")
    # ###############################################################################################################
    with rasterio.open(example_tif) as src:
        raster_crs = src.crs
    
    print(f"SHP坐标系: {gdf.crs}")
    print(f"TIF坐标系: {raster_crs}")
    
    if gdf.crs != raster_crs:
        print("坐标系不一致，自动转换！")
        gdf = gdf.to_crs(raster_crs)
    else:
        print("坐标系一致，无需转换。")

    # 获取shp的年份列表
    years = sorted(gdf['YEAR_'].unique())

    for year in years:
        try:
            print(f'开始处理年份：{year}')
            
            # 筛选该年份所有面要素
            gdf_year = gdf[gdf['YEAR_'] == year]
            if gdf_year.empty:
                print(f'年份 {year} 没有面要素')
                continue
            ####################################################################################################
            # 查找对应年份的.tif文件
            tif_pattern = os.path.join(tif_folder, f'CStocks_Live_{year}.tif')
            # ###############################################################################################################
            if not os.path.exists(tif_pattern):
                print(f'缺少该年的tif文件：{tif_pattern}')
                error_years.append(year)
                continue

            # 打开并裁剪
            with rasterio.open(tif_pattern) as src:
                out_image, out_transform = mask(
                    src, gdf_year.geometry, crop=True, nodata=src.nodata)
                out_meta = src.meta.copy()

            # 更新输出的tif信息
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })

            # 输出
            # ###############################################################################################################
            out_fp = os.path.join(output_folder, f'AGB{year}_clip.tif')
            # ###############################################################################################################
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
    print(f'总共处理年份数: {len(years)}')
    print(f'成功裁剪TIF数量: {successful_tifs}')
    
    if error_years:
        print(f'处理失败的年份: {error_years}')
    
    print('多要素剪裁时序栅格处理完成！')