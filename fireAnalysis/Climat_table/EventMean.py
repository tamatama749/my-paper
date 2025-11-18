import pandas as pd

# 1. 读取原始CSV文件
input_path = r'E:/CA_Fire_Analysis3/Yr_wui_event_P/statistTable/WUIfire_SPEI4km_YR_result.csv'
df = pd.read_csv(input_path)

# 2. 筛选所需字段，去除'OID_'字段
columns_to_use = [col for col in df.columns if col != 'OID_']
df = df[columns_to_use]

# 3. 将所有-9999的异常值替换为NaN（空值）
# 注意：这里要在转换数据类型之前进行替换
df = df.replace(-9999, pd.NA)
df = df.replace(0, pd.NA)

# 4. 按火事件编号'OBJECTID'分组，对气象信息取均值
agg_dict = {'YEAR_': 'first'}
# 其余字段均取均值（除去OBJECTID和YEAR_）
for col in df.columns:
    if col not in ['OBJECTID', 'YEAR_']:
        agg_dict[col] = 'mean'

# 分组并聚合
result = df.groupby('OBJECTID', as_index=False).agg(agg_dict)

# 5. 对所有数值列保留5位小数（在保存前进行）
float_cols = result.select_dtypes(include=['float', 'float64', 'float32']).columns.tolist()
result[float_cols] = result[float_cols].round(5)

# 6. 保存CSV文件 - 关键修改点
output_path = r'E:\CA_Fire_Analysis3\Yr_wui_event_P\statistTable\WUIEvent_SPEInew_mean.csv'

# 方案1：使用标准的float_format（推荐）
result.to_csv(output_path, index=False, encoding='utf-8-sig', float_format='%.5f')
# 如果方案1还有问题，使用方案2：手动格式化后保存
# 创建一个副本用于输出
# result_output = result.copy()
# for col in float_cols:
#     result_output[col] = result_output[col].apply(lambda x: f"{x:.5f}" if pd.notnull(x) else "")
# result_output.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"处理完成，合并后的数据已保存至: {output_path}")
print(f"原始数据行数: {len(df)}")
print(f"合并后数据行数: {len(result)}")
print(f"注意：计算均值时已自动排除-9999异常值，所有数值已保留5位小数")