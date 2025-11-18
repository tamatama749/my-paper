import geopandas as gpd
import pandas as pd
import os

# 指定存放.shp文件的目录
shp_directory = r'E:\CA_Fire_Analysis3\GlobalFireAtlas\ignitionP'  # 已替换为你的.shp文件目录
output_file = 'point_counts.csv'


# 用列表收集结果，最后构造DataFrame
result_list = []

# 遍历.shp文件，统计每个文件中的点要素数量
for filename in os.listdir(shp_directory):
    if filename.endswith('.shp'):
        file_path = os.path.join(shp_directory, filename)
        # 读取.shp文件
        gdf = gpd.read_file(file_path)

        # 检查点要素
        if gdf.geom_type.isin(['Point']).any():
            point_count = gdf[gdf.geom_type == 'Point'].shape[0]
        else:
            point_count = 0
        # 将结果添加到列表
        result_list.append({'filename': filename, 'point_count': point_count})


# 列表转DataFrame并保存
results = pd.DataFrame(result_list, columns=[year, 'point_count'])
results.to_csv(output_file, index=False)

print(f'点要素数量已保存到 {os.path.abspath(output_file)}')