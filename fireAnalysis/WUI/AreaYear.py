import pandas as pd  
import matplotlib.pyplot as plt  
import numpy as np  

# 读取数据文件，假设文件名为 'fire_data.csv'  
file_path = ('E:/CA_Fire_Analysis/WUI/cityAnaly/SF.csv')  # 请根据实际文件名和路径进行修改  
data = pd.read_csv(file_path, encoding='utf-8')  

# 确保列名与数据文件中的一致  
# 计算逐年两种区域的燃烧总面积  
yearly_area = data.groupby('YEAR_').agg({  
    'facePixel_100m(m2': 'sum',  
    'mixPixel_100m(m2': 'sum'  
}).reset_index()  

