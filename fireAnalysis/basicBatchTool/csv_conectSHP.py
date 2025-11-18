import shapefile
import pandas as pd
import shutil
import os

# 路径定义
source_shp = r"E:/CA_Fire_Analysis3/4typeEvents/new/polygon/I-W207_poly.shp"  # 输入：提供OBJECTID的shapefile
target_shp = r"E:/CA_Fire_Analysis3/4typeEvents/burnWUIchange/all_05km2event_30mBwui_ChangeP"  # 输入：被搜索的shapefile（点\线\面都可以）
output_shp = r"E:/CA_Fire_Analysis3/4typeEvents/burnWUIchange/02_23burnWUI_30mchangeP_I-W.shp"  # 输出：匹配结果

print("=" * 60)
print("根据源文件的OBJECTID筛选目标文件")
print("=" * 60)

# 1. 读取源文件，提取OBJECTID
print(f"\n[步骤1] 读取源文件: {source_shp}")
sf_source = shapefile.Reader(source_shp)
records_source = sf_source.records()
df_source = pd.DataFrame([rec.as_dict() for rec in records_source])

# 检查字段
if 'OBJECTID' not in df_source.columns:
    print(f"错误: 源文件中未找到'OBJECTID'字段!")
    print(f"可用字段: {list(df_source.columns)}")
    exit()

# 获取所有需要匹配的OBJECTID值
target_objectids = set(df_source['OBJECTID'].values)
print(f"源文件共 {len(records_source)} 个要素")
print(f"包含 {len(target_objectids)} 个不同的OBJECTID值")
print(f"OBJECTID示例: {list(target_objectids)[:10]}")

# 2. 读取目标文件
print(f"\n[步骤2] 读取目标文件: {target_shp}")
sf_target = shapefile.Reader(target_shp)
records_target = sf_target.records()
shapes_target = sf_target.shapes()
df_target = pd.DataFrame([rec.as_dict() for rec in records_target])

# 检测几何类型
shape_type = sf_target.shapeType
shape_type_names = {
    1: "点", 3: "线", 5: "面", 
    8: "多点", 11: "点Z", 13: "线Z", 15: "面Z",
    21: "点M", 23: "线M", 25: "面M"
}
geom_type = shape_type_names.get(shape_type, f"类型{shape_type}")
print(f"目标文件共 {len(records_target)} 个要素（几何类型: {geom_type}）")

#########################################################################
# 检查字段
if 'OBJECTID' not in df_target.columns:
    print(f"错误: 目标文件中未找到'OBJECTID'字段!")
    print(f"可用字段: {list(df_target.columns)}")
    exit()
#########################################################################
# 3. 匹配，注意修改目标字段的列名
print(f"\n[步骤3] 根据OBJECTID匹配要素...")
match_mask = df_target['OBJECTID'].isin(target_objectids)
match_indices = match_mask[match_mask].index.tolist()

print(f"✓ 找到 {len(match_indices)} 个匹配的要素")

if len(match_indices) == 0:
    print("\n警告: 没有找到匹配的要素!")
    exit()

# 4. 保存匹配的要素
print(f"\n[步骤4] 保存到: {output_shp}")
w_output = shapefile.Writer(output_shp)
w_output.fields = sf_target.fields[1:]  # 复制字段结构

for idx in match_indices:
    w_output.record(*records_target[idx])
    w_output.shape(shapes_target[idx])

w_output.close()

# 5. 复制.prj投影文件
prj_src = target_shp.replace('.shp', '.prj')
prj_dst = output_shp.replace('.shp', '.prj')
if os.path.exists(prj_src):
    shutil.copy2(prj_src, prj_dst)
    print("✓ 已复制投影文件(.prj)")

print("\n" + "=" * 60)
print("✓✓✓ 任务完成! ✓✓✓")
print("=" * 60)
print(f"\n结果:")
print(f"- 源文件要素数: {len(records_source)} 个")
print(f"- 目标文件要素数: {len(records_target)} 个 ({geom_type})")
print(f"- 匹配输出要素数: {len(match_indices)} 个")
print(f"- 输出文件: {output_shp}")

#########################################################################
# 显示匹配的OBJECTID统计
matched_objectids = set(df_target.loc[match_indices, 'OBJECTID'].values)
unmatched_objectids = target_objectids - matched_objectids

print(f"\n" + "=" * 60)
print("匹配统计:")
print("=" * 60)
print(f"- 源文件中的OBJECTID总数: {len(target_objectids)}")
print(f"- 成功匹配的OBJECTID数量: {len(matched_objectids)}")
print(f"- 未匹配的OBJECTID数量: {len(unmatched_objectids)}")

# 打印未匹配的OBJECTID
if len(unmatched_objectids) > 0:
    print(f"\n⚠️ 未匹配的OBJECTID值（共{len(unmatched_objectids)}个）:")
    print("-" * 60)
    
    # 将未匹配的值排序后打印
    unmatched_list = sorted(list(unmatched_objectids))
    
    # 如果数量较少，全部打印
    if len(unmatched_list) <= 50:
        for i, obj_id in enumerate(unmatched_list, 1):
            print(f"{i:3d}. {obj_id}")
    else:
        # 如果数量太多，打印前30个和后20个
        print("前30个:")
        for i, obj_id in enumerate(unmatched_list[:30], 1):
            print(f"{i:3d}. {obj_id}")
        
        print(f"\n... (中间省略 {len(unmatched_list) - 50} 个) ...\n")
        
        print("后20个:")
        for i, obj_id in enumerate(unmatched_list[-20:], len(unmatched_list) - 19):
            print(f"{i:3d}. {obj_id}")
    
    # # 可选：保存到文本文件
    # unmatched_file = output_shp.replace('.shp', '_unmatched_objectids.txt')
    # with open(unmatched_file, 'w', encoding='utf-8') as f:
    #     f.write(f"未匹配的OBJECTID列表（共{len(unmatched_list)}个）\n")
    #     f.write("=" * 60 + "\n\n")
    #     for i, obj_id in enumerate(unmatched_list, 1):
    #         f.write(f"{i}. {obj_id}\n")
    
    # print(f"\n✓ 未匹配列表已保存到: {unmatched_file}")
    
else:
    print(f"\n✅ 太棒了！所有OBJECTID都成功匹配！")