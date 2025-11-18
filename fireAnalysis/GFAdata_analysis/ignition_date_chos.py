import geopandas as gpd
import pandas as pd
import numpy as np

# 读取矢量文件
file_path = r"E:/CA_Fire_Analysis3/GlobalFireAtlas/ignt_WILDevent/Wild_1kmbuffer_clipped_ignitions_merged.shp"
gdf = gpd.read_file(file_path)

# 将 ALARM_DATE 转换为日期格式
gdf['ALARM_DATE'] = pd.to_datetime(gdf['ALARM_DATE']).dt.strftime('%Y-%m-%d')

# 计算当年的儒略日（Day of Year）
gdf['FARP_DOY'] = gdf['ALARM_DATE'].apply(lambda x: pd.to_datetime(x).dayofyear)

# 将 FARP_DOY 保留为双精度数值型并取整
gdf['FARP_DOY'] = gdf['FARP_DOY'].astype(np.float64).round(0)

# 保存文件
gdf.to_file(file_path, driver='ESRI Shapefile')