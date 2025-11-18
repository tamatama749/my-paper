import pandas as pd
import numpy as np

# ============================================================
# 优化版：适合处理大文件（数十万行数据）
# 支持缺失年份数据用 -9999 标记
# tdmean10 = (当年 + 前1年) / 2
# tdmean20 = (当年 + 前1年 + 前2年) / 3
# ============================================================

# 第一步：读取Excel文件
input_file = r'E:\CA_Fire_Analysis3\Yr_wui_event_P\statistTable\WUIeventArtubt_SPEI2023.csv'  # 修改为你的文件路径
# input_file = r'E:\CA_Fire_Analysis2\codetest\WUIfireClimt_test.xlsx'  # 小样本数据测试
print("="*60)
print("开始读取csv文件...")
print(f"文件路径: {input_file}")
print("请耐心等待，大文件可能需要几分钟...")
print("="*60)

df = pd.read_csv(input_file)

print(f"✓ 文件读取完成！")


print(f"原始数据行数: {len(df)}")
print(f"原始数据列数: {len(df.columns)}")

# 第二步：定义需要处理的气象变量前缀列表
# *** 这里可以修改气象变量名称 ***
var_prefixes = [
    'SPE12_','SPE06_','SPE03_','SPE01_'
]

# *** 这里可以修改异常值标记 ***
MISSING_VALUE = -9999  # 缺失数据的标记值，可以改成其他值如 -999 或 None

print(f"\n将要处理的气象变量: {var_prefixes}")
print(f"缺失数据标记值: {MISSING_VALUE}")

# 第三步：创建结果DataFrame
result_df = df[['OID_', 'OBJECTID', 'YEAR_']].copy()

# 第四步：使用向量化操作处理（速度更快）
print("\n开始处理气象变量...")

for var_prefix in var_prefixes:
    print(f"\n正在处理: {var_prefix}")
    
    # 创建新列
    col_year0 = f'{var_prefix}0'     # 当年值
    
    # 初始化为 -9999
    result_df[col_year0] = MISSING_VALUE

    
    # 统计缺失列的计数器
    missing_count_0 = 0

    
    # 获取该变量所有年份的列（1998-2023）
    year_cols = [col for col in df.columns if col.startswith(var_prefix) and col[len(var_prefix):].isdigit()]
    
    # 为每个可能的年份创建映射
    for year in range(2002, 2023):  # 根据你的数据范围调整
        # 构造列名
        col_year0_original = f'{var_prefix}{year}'      # 当年列名

        # 找到该年份的所有行
        mask = (df['YEAR_'] == year)
        
        if mask.any():
            # ============================================================
            # *** 修改点：这里是核心计算逻辑 ***
            # ============================================================
            
            # 1. 当年数据（tdmean0）- 直接取当年值
            if col_year0_original in df.columns:
                result_df.loc[mask, col_year0] = df.loc[mask, col_year0_original].fillna(MISSING_VALUE)
            else:
                missing_count_0 += mask.sum()
    
    # 统计信息
    valid_count_0 = (result_df[col_year0] != MISSING_VALUE).sum()

    print(f"  - {col_year0} (当年值):")
    print(f"      有效数据: {valid_count_0} 行")
    print(f"      缺失数据（标记为{MISSING_VALUE}）: {missing_count_0} 行")
    

# 第五步：查看结果
print("\n" + "="*60)
print("处理完成！")
print("="*60)
print(f"\n结果数据: {len(result_df)} 行 × {len(result_df.columns)} 列")
print("\n前10行预览：")
print(result_df.head(10))

# 显示整体缺失情况统计
print("\n" + "="*60)
print("整体缺失数据统计：")
print("="*60)
for col in result_df.columns:
    if col not in ['OID_', 'OBJECTID', 'YEAR_']:
        missing = (result_df[col] == MISSING_VALUE).sum()
        if missing > 0:
            print(f"{col}: {missing} 行缺失（占比 {missing/len(result_df)*100:.2f}%）")

# 第六步：导出
output_file = 'E:/CA_Fire_Analysis3/Yr_wui_event_P/statistTable/WUIfire_SPEI4km_YR_result2023.csv'
result_df = result_df.round(5)
result_df.to_csv(output_file, index=False)
print(f"\n✅ 数据已导出到: {output_file}")
print(f"注意：缺失的气象数据已用 {MISSING_VALUE} 标记")