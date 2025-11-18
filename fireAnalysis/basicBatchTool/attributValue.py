import shapefile
import os

# 路径定义
input_shp = r"E:/CA_Fire_Analysis3/4typeEvents/new/I-W207_poly.shp"  # 输入文件
output_shp = r"E:/CA_Fire_Analysis3/4typeEvents/new/I-W207_poly.shp"  # 输出文件（可以与输入相同来覆盖）

print("=" * 60)
print("为shapefile添加新字段并赋值")
print("=" * 60)

# 1. 读取原始shapefile
print(f"/n[步骤1] 读取文件: {input_shp}")
sf = shapefile.Reader(input_shp)
records = sf.records()
shapes = sf.shapes()
fields = sf.fields[1:]  # 获取字段定义（跳过DeletionFlag）

print(f"共 {len(records)} 个要素")
print(f"原有字段: {[field[0] for field in fields]}")

# 2. 创建新的shapefile写入器
print(f"/n[步骤2] 创建新文件: {output_shp}")
w = shapefile.Writer(output_shp)

# 3. 复制原有字段结构
for field in fields:
    w.field(*field)

# 4. 添加新字段 eventTYPE（文本型，长度50）
w.field('eventTYPE', 'C', size=50)  # 'C' = Character/文本型
print("✓ 已添加字段: eventTYPE (文本型, 长度50)")

# 5. 写入所有要素（复制原有数据 + 添加新字段值）
print(f"/n[步骤3] 为所有要素赋值 'I-W'...")
for i, (record, shape) in enumerate(zip(records, shapes)):
    # 复制原有属性
    new_record = list(record)
    # 添加新字段的值
    new_record.append('I-W')
    
    # 写入记录和几何
    w.record(*new_record)
    w.shape(shape)
    
    # 进度显示
    if (i + 1) % 100 == 0 or (i + 1) == len(records):
        print(f"进度: {i + 1}/{len(records)}")

# 6. 关闭写入器
w.close()
print("✓ 数据写入完成")

# 7. 复制投影文件（修复：判断是否同一文件）
prj_src = input_shp.replace('.shp', '.prj')
prj_dst = output_shp.replace('.shp', '.prj')

# 转换为绝对路径比较
prj_src_abs = os.path.abspath(prj_src)
prj_dst_abs = os.path.abspath(prj_dst)

if prj_src_abs != prj_dst_abs:  # 只有不同文件才复制
    if os.path.exists(prj_src):
        shutil.copy2(prj_src, prj_dst)
        print("✓ 已复制投影文件(.prj)")
else:
    print("✓ 输入输出为同一文件，跳过投影文件复制")

# 8. 如果需要覆盖原文件
if input_shp == output_shp:
    print("/n⚠️ 注意: 已覆盖原文件")

print("/n" + "=" * 60)
print("✓✓✓ 任务完成! ✓✓✓")
print("=" * 60)

# 验证结果
print(f"/n[验证] 读取新文件验证...")
sf_new = shapefile.Reader(output_shp)
new_fields = [field[0] for field in sf_new.fields[1:]]
print(f"新文件字段: {new_fields}")

# 读取第一条记录验证
first_record = sf_new.records()[0]
record_dict = first_record.as_dict()
print(f"/n第一条记录示例:")
for key, value in record_dict.items():
    print(f"  {key}: {value}")