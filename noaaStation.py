import pandas as pd
import numpy as np
path_tif = "H:/basicData/NOAA/"  # 设置路径

data1=pd.DataFrame(pd.read_excel(path_tif+'fireTable.xlsx'))
data1=data1.drop(labels=['lat','lon','x_','y_','tan','direction','year','value',
                         	'majBurn_DATE'	,'contrast',	'min',	'max'	,'count',
                        'std',	'median',	'majority',	'range_',	'range'	,'centerX',	'centerY'
],axis=1)
data2=pd.DataFrame(pd.read_csv(path_tif+'3149094_new.csv'))
for colume_name,item in data2.iteritems():
	for i in item.index:
		if item[i]==9999.9 or item[i]==99.99 or item[i]==999.9:
			item[i]=item[i-1]
	# print("re", i)
# data2.to_csv("clean_data.csv")





loan_inner=pd.merge(data1,data2,how='inner',left_on='START_DATE',right_on='DATE')#按照data1 data2相同字段合并表格

duplicate_bool = loan_inner.duplicated(subset=['START_DATE'], keep='first')
date_data = []


series = duplicate_bool[duplicate_bool.values == False].index#查找表格中重复字段，并返回索引

for i in range(len(series)):#用列表形式依次保存重复的字段
    if not series[i] == series[-1]:
        date_data.append(loan_inner[series[i]:series[i + 1] - 1])
    else:
        date_data.append(loan_inner[series[i]:])

for j in range(len(date_data)):#循环输出保存文件
    print(date_data[j].START_DATE[date_data[j].START_DATE.index[0]])
    date_data[j].to_csv(r'{}.csv'.format(date_data[j].START_DATE[date_data[j].START_DATE.index[0]].replace('/','-')))


for index in duplicate_bool:
    print(index)








