import shapefile
import pandas as pd

# 路径定义
point_shp = r"E:/CA_Fire_Analysis3/4typeEvents/merge4type1100_copy.shp"
point_out_shp = r"E:/CA_Fire_Analysis3/4typeEvents/multiGFA.shp"
polygon_shp = r"E:/CA_Fire_Analysis3/02-23fire/eventWUI_haveGFApoint_981.shp"
polygon_out_shp = r"E:/CA_Fire_Analysis3/4typeEvents/multiGFA_Event.shp"

print("=" * 60)
print("使用pyshp处理shapefile...")
print("=" * 60)

# 1. 读取点数据
print("\n[步骤1] 读取点要素...")
sf_point = shapefile.Reader(point_shp)
records_point = sf_point.records()
shapes_point = sf_point.shapes()
fields_point = sf_point.fields[1:]  # 跳过DeletionFlag
field_names = [field[0] for field in fields_point]

print(f"字段: {field_names}")
print(f"共 {len(records_point)} 个点要素")

# 转为DataFrame
df_point = pd.DataFrame([rec.as_dict() for rec in records_point])

# 检查字段
if 'OBJECTID_1' not in df_point.columns:
    print(f"错误: 未找到OBJECTID_1字段!")
    print(f"可用字段: {list(df_point.columns)}")
    exit()

# 2. 找重复
print("\n[步骤2] 查找重复...")
repeat_mask = df_point['OBJECTID_1'].duplicated(keep=False)
duplicate_indices = repeat_mask[repeat_mask].index.tolist()

print(f"找到 {len(duplicate_indices)} 个重复要素")

# 3. 保存重复的点
print(f"\n[步骤3] 保存到 {point_out_shp}...")
w_point = shapefile.Writer(point_out_shp)
w_point.fields = sf_point.fields[1:]

for idx in duplicate_indices:
    w_point.record(*records_point[idx])
    w_point.shape(shapes_point[idx])

w_point.close()

# 复制.prj文件
import shutil, os
prj_src = point_shp.replace('.shp', '.prj')
prj_dst = point_out_shp.replace('.shp', '.prj')
if os.path.exists(prj_src):
    shutil.copy2(prj_src, prj_dst)

print("✓ 点要素保存成功!")

# 4. 读取面数据
print("\n[步骤4] 读取面要素...")
sf_poly = shapefile.Reader(polygon_shp)
records_poly = sf_poly.records()
shapes_poly = sf_poly.shapes()

df_poly = pd.DataFrame([rec.as_dict() for rec in records_poly])
print(f"共 {len(records_poly)} 个面要素")

# 5. 匹配
print("\n[步骤5] 匹配面要素...")
dup_objectids = set(df_point.loc[duplicate_indices, 'OBJECTID_1'].values)
match_mask = df_poly['OBJECTID_1'].isin(dup_objectids)
match_indices = match_mask[match_mask].index.tolist()

print(f"找到 {len(match_indices)} 个匹配面要素")

# 6. 保存
print(f"\n[步骤6] 保存到 {polygon_out_shp}...")
w_poly = shapefile.Writer(polygon_out_shp)
w_poly.fields = sf_poly.fields[1:]

for idx in match_indices:
    w_poly.record(*records_poly[idx])
    w_poly.shape(shapes_poly[idx])

w_poly.close()

# 复制.prj文件
prj_src_poly = polygon_shp.replace('.shp', '.prj')
prj_dst_poly = polygon_out_shp.replace('.shp', '.prj')
if os.path.exists(prj_src_poly):
    shutil.copy2(prj_src_poly, prj_dst_poly)

print("✓ 面要素保存成功!")

print("\n" + "=" * 60)
print("✓✓✓ 完成! ✓✓✓")
print("=" * 60)