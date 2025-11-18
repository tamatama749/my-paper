import os

wui_folder = r"E:\data\CA_FIRE\CA_WUI\merge2WUIshp\CRS_trans"
year = 2020
potential_path = os.path.join(wui_folder, f"WUI{year}.shp")

print(f"检查文件: {potential_path}")
print(f"文件存在: {os.path.exists(potential_path)}")

# 尝试另一种方式
potential_path2 = f"{wui_folder}\\WUI{year}.shp"
print(f"检查文件2: {potential_path2}")
print(f"文件存在2: {os.path.exists(potential_path2)}")

# 列出目录内容看看
try:
    files = os.listdir(wui_folder)
    wui_files = [f for f in files if f.startswith("WUI2020")]
    print(f"找到的2020年WUI文件: {wui_files}")
except Exception as e:
    print(f"列出目录错误: {e}")