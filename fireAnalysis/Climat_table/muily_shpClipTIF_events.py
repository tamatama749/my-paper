import os
import glob
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import pandas as pd

# ------------------ 配置区：根据实际情况修改路径------------------
# 1. shp矢量文件路径
shp_path = r'E:/CA_Fire_Analysis3/4typeEvents/new/polygon/merge_4tpyeEvent_Poly.shp'

# 2. 栅格数据文件夹（所有待逐年裁剪的tif文件都在这里）
tif_folder = r'E:/data/NLCD_USA'

# 3. 输出裁剪后栅格的文件夹
output_folder = r'E:/CA_Fire_Analysis3/Yr_wui_event_P/fuel_event'

# 4. 输出统计CSV文件路径
output_csv = os.path.join(output_folder, 'WUI_LC_events_statistics.csv')

# 5. 选择剪裁模式：'next' 表示用当前年份shp剪裁下一年tif，'prev' 表示用当前年份shp剪裁上一年tif
clip_mode = 'prev'  # 或 改为'next'

# 6. 是否保存裁剪后的tif文件（如果只需要统计信息，可设为False节省空间）
save_clipped_tif = False  # 改为False则不保存tif

# ------------------ 主程序 ------------------
# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 初始化统计列表
statistics_list = []
error_records = []
successful_count = 0

try:
    # 读取矢量面shp
    gdf = gpd.read_file(shp_path)
    
    # 检查必要字段
    if 'YEAR_' not in gdf.columns or 'OBJECTID' not in gdf.columns:
        raise ValueError("SHP文件缺少必要字段：YEAR_ 或 OBJECTID")
    
    # 随便找一年tif读取其投影
    example_tif = os.path.join(tif_folder, "Annual_NLCD_LndCov_2023_CU_C1V0.tif")
    
    with rasterio.open(example_tif) as src:
        raster_crs = src.crs
        raster_nodata = src.nodata
    
    print(f"SHP坐标系: {gdf.crs}")
    print(f"TIF坐标系: {raster_crs}")
    print(f"TIF NoData值: {raster_nodata}")
    
    # 坐标系转换
    if gdf.crs != raster_crs:
        print("坐标系不一致，自动转换！")
        gdf = gdf.to_crs(raster_crs)
    else:
        print("坐标系一致，无需转换。")

    # 获取所有年份
    years = sorted(gdf['YEAR_'].unique())
    print(f"\n共有 {len(years)} 个年份需要处理")
    print(f"年份范围: {min(years)} - {max(years)}")
    
    # 总要素数
    total_features = len(gdf)
    print(f"总共 {total_features} 个要素\n")

    # 逐要素处理
    for idx, row in gdf.iterrows():
        try:
            year = row['YEAR_']
            objectid = row['OBJECTID']
            geometry = row['geometry']
            
            print(f'[{idx+1}/{total_features}] 处理 OBJECTID: {objectid}, 年份: {year}')
            
            # 确定目标年份
            if clip_mode == 'next':
                target_year = year + 1
            elif clip_mode == 'prev':
                target_year = year - 1
            else:
                raise ValueError(f"无效的clip_mode: {clip_mode}")
            
            # 查找目标年份的tif文件
            tif_path = os.path.join(tif_folder, f'Annual_NLCD_LndCov_{target_year}_CU_C1V0.tif')
            
            if not os.path.exists(tif_path):
                print(f'  ⚠ 缺少目标年份 {target_year} 的tif文件，跳过')
                error_records.append({
                    'OBJECTID': objectid,
                    'YEAR': year,
                    'TARGET_YEAR': target_year,
                    'ERROR': 'TIF文件不存在'
                })
                continue

            # 打开tif并裁剪
            with rasterio.open(tif_path) as src:
                # 用单个要素进行裁剪
                out_image, out_transform = mask(
                    src, [geometry], crop=True, nodata=src.nodata
                )
                out_meta = src.meta.copy()
            
            # 提取栅格数据（第一个波段）
            raster_data = out_image[0]
            
            # 统计不同像元值个数（排除nodata）
            if raster_nodata is not None:
                valid_data = raster_data[raster_data != raster_nodata]
            else:
                # 如果没有nodata，可能需要排除nan
                valid_data = raster_data[~np.isnan(raster_data)]
            
            # 获取唯一值及其个数
            unique_values, counts = np.unique(valid_data, return_counts=True)
            num_unique_values = len(unique_values)
            
            # # 统计信息
            # stats = {
            #     'OBJECTID': objectid,
            #     'YEAR': year,
            #     'TARGET_YEAR': target_year,
            #     'UNIQUE_PIXEL_VALUES': num_unique_values,
            #     'TOTAL_VALID_PIXELS': len(valid_data),
            #     'MIN_VALUE': float(np.min(valid_data)) if len(valid_data) > 0 else np.nan,
            #     'MAX_VALUE': float(np.max(valid_data)) if len(valid_data) > 0 else np.nan,
            #     'MEAN_VALUE': float(np.mean(valid_data)) if len(valid_data) > 0 else np.nan,
            #     'STD_VALUE': float(np.std(valid_data)) if len(valid_data) > 0 else np.nan
            # }
            stats = {
            'OBJECTID': objectid,
            'YEAR': year,
            'TARGET_YEAR': target_year,
            'UNIQUE_PIXEL_VALUES': num_unique_values,
            'TOTAL_VALID_PIXELS': len(valid_data)
            }

            # 将每个像元值及其计数添加为单独的列
            for value, count in zip(unique_values, counts):
                stats[f'LC_{value}'] = int(count)

            # # 统计信息

            statistics_list.append(stats)

            
            # 保存裁剪后的tif（可选）
            if save_clipped_tif:
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })
                
                out_fp = os.path.join(
                    output_folder, 
                    f'OBJECTID{objectid}_{year}.tif'
                )
                
                with rasterio.open(out_fp, "w", **out_meta) as dest:
                    dest.write(out_image)
                
                print(f'  ✓ 已保存: {os.path.basename(out_fp)}')
            
            successful_count += 1

        except Exception as feature_error:
            print(f'  ✗ 处理 OBJECTID {objectid} 时发生错误: {str(feature_error)}')
            error_records.append({
                'OBJECTID': objectid,
                'YEAR': year,
                'TARGET_YEAR': target_year if 'target_year' in locals() else 'N/A',
                'ERROR': str(feature_error)
            })

except Exception as e:
    print(f'\n❌ 处理过程中发生严重错误: {str(e)}')

finally:
    # 保存统计结果到CSV
    if statistics_list:
        df_stats = pd.DataFrame(statistics_list)
        df_stats.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f'\n✓ 统计结果已保存至: {output_csv}')
        print(f'\n统计摘要:')
        print(df_stats.describe())
    else:
        print('\n⚠ 没有成功处理任何要素，无法生成统计CSV')
    
    # 保存错误记录
    if error_records:
        error_csv = os.path.join(output_folder, 'error_records.csv')
        df_errors = pd.DataFrame(error_records)
        df_errors.to_csv(error_csv, index=False, encoding='utf-8-sig')
        print(f'\n⚠ 错误记录已保存至: {error_csv}')
    
    # 打印处理总结
    print('\n' + '='*60)
    print(f'总要素数: {total_features}')
    print(f'成功处理: {successful_count}')
    print(f'失败数量: {len(error_records)}')
    print('='*60)
    print('✓ 处理完成！')