import rasterio
import numpy as np

# 输入和输出文件路径
input_file = 'E:/CA-Biomass/CECS/CStocks_Live202211/CStocks_Live_1996.tif'
output_file = 'E:/CA_Fire_Analysis2/codetest/output1996.tif'

# 步骤 1: 读取 TIFF 文件
with rasterio.open(input_file) as dataset:
    # 打印元数据
    print(f"Driver: {dataset.driver}")
    print(f"Width: {dataset.width}, Height: {dataset.height}")
    print(f"Count: {dataset.count}")
    print(f"CRS: {dataset.crs}")
    print(f"Transform: {dataset.transform}")
    
    # 步骤 2: 获取数据
    data = dataset.read(1)  # 读取第一波段
    nodata_value = dataset.nodata  # 获取 NoData 值
    print(f"NoData value: {nodata_value}")

    # 步骤 3: 检查 NoData 区域数量
    if nodata_value is not None:
        no_data_count = np.sum(data == nodata_value)
        print(f"NoData count: {no_data_count}")
        
        # 输出 NoData 范围的统计信息
        if no_data_count > 0:
            print("存在 NoData 区域，继续检测如何修复...")
            no_data_percentage = (no_data_count / data.size) * 100
            print(f"NoData 区域占比: {no_data_percentage:.2f}%")
            
            # 判断如何修复
            if no_data_percentage > 5:
                print("NoData 区域占比较高，考虑使用周围像元值进行填充。")
                # 简单填充示例（平均值填充）
                mean_value = np.nanmean(np.where(data != nodata_value, data, np.nan))
                print(f"用平均值 {mean_value} 填充 NoData 区域。")
                data[data == nodata_value] = mean_value  # 用平均值进行填充
            else:
                print("NoData 区域占比较低，考虑简单替换为 0。")
                data[data == nodata_value] = 0  # 替换为 0
    
    else:
        print("未定义 NoData 值，所有区域均有有效数据。")