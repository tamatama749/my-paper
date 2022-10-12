import gdal
import os
import numpy as np
import pandas as pd
import matplotlib

from sklearn.cluster import DBSCAN
from sklearn import metrics
# import seaborn as sns
from sklearn.cluster import OPTICS
from spectral_clustering import chose_para
from sklearn.datasets import make_classification
from sklearn.mixture import GaussianMixture
from numpy import unique
from numpy import where
from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator
from sklearn.preprocessing import normalize

def arr2raster(arr, raster_file, prj=None, trans=None):
	"""
	将数组转成栅格文件写入硬盘
	:param arr: 输入的mask数组 ReadAsArray()
	:param raster_file: 输出的栅格文件路径
	:param prj: gdal读取的投影信息 GetProjection()，默认为空
	:param trans: gdal读取的几何信息 GetGeoTransform()，默认为空
	:return:
	"""

	driver = gdal.GetDriverByName('GTiff')
	dst_ds = driver.Create(raster_file, arr.shape[1], arr.shape[0], 1, gdal.GDT_Byte)

	if prj:
		dst_ds.SetProjection(prj)
	if trans:
		dst_ds.SetGeoTransform(trans)

	# 将数组的各通道写入图片
	dst_ds.GetRasterBand(1).WriteArray(arr)

	dst_ds.FlushCache()
	dst_ds = None
	print("successfully convert array to raster")

#建立聚类模型
def dbscan_cluster(data_norm,eps):
	print("start dbscan")
	print("eps_number", a)
	dbscan_result = DBSCAN(eps=eps, min_samples=4).fit_predict(data_norm)
	matrix = np.zeros((data_x, data_y))  # 初始化0矩阵,之后可以加你想要的值
	matrix = matrix + 200
	for i in range(kmeans_xy.shape[0]):
		matrix[kmeans_xy[i][0]][kmeans_xy[i][1]] = dbscan_result[i]


	db = DBSCAN(eps=eps, min_samples=4).fit(data_norm)  # DBSCAN聚类方法 还有参数，matric = ""距离计算方法
	pd_data = pd.DataFrame(data_norm)
	pd_data.columns = ['x', 'y','z']
	pd_data['labels'] = db.labels_  # 和X同一个维度，labels对应索引序号的值 为她所在簇的序号。若簇编号为-1，表示为噪声，我们把标签放回到data数据集中方便画图
	labels = db.labels_
	raito = pd_data.loc[pd_data['labels'] == -1].x.count() / pd_data.x.count()  # labels=-1的个数除以总数，计算噪声点个数占总数的比例
	print('噪声比:', format(raito, '.2%'))
	n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)  # 获取分簇的数目
	print('分簇的数目: %d' % n_clusters_)
	print("轮廓系数: %0.3f" % metrics.silhouette_score(pd_data, labels))  # 轮廓系数评价聚类的好坏



	return matrix

os.chdir('H:/basicData/MCD64A1_output/DXAL_mcd64a1/jenks/')   #更改当前工作路径
index_number = str('2020_2')
m = 5
dataset = gdal.Open("reclass_dxal_MCD64A1_"+index_number+".tif")

# BBand = dataset.GetRasterBand(band)
XSize = dataset.RasterXSize  # 网格的X轴像素数量
YSize = dataset.RasterYSize  # 网格的Y轴像素数量
im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
im_proj = dataset.GetProjection()  # 地图投影信息
data = dataset.ReadAsArray(0, 0, XSize, YSize).astype(np.float32)
data_x = data.shape[0]
data_y= data.shape[1]
data_days = data.ravel()[np.flatnonzero(data)]
kmeans_xy = np.nonzero(data)
kmeans_xy = np.array(kmeans_xy)
kmeans_xy = kmeans_xy.T
kmeans_xyd = np.insert(kmeans_xy,2,data_days,1)
print(kmeans_xyd.shape)
data_norm=normalize(kmeans_xyd,axis=0,norm='max')
# data_norm=normalize(kmeans_xyd,axis=2,norm='max')


#方法一：k_dist图选取eps

plt.rc('font',family='Times New Roman',size= 20)
def select_MinPts(data_norm,k):
    k_dist = []
    for i in range(data_norm.shape[0]):
        dist = (((data_norm[i] - data_norm)**2).sum(axis=1)**0.5)
        dist.sort()
        k_dist.append(dist[k])
    return np.array(k_dist)
k = 3  # 此处k取 2*维度 -1，维度为特征数
k_dist = select_MinPts(data_norm,k)
k_dist.sort()


matplotlib.rc("font",family='DengXian') # 设置字体

plt.figure(figsize=(6, 4)) # 设置图幅大小
plt.plot(np.arange(k_dist.shape[0]),k_dist[::-1], label='k-距离') #绘制曲线
plt.title(index_number) #设置标题


eps = k_dist[::-1][m]
a = eval("%.3f"%eps)
plt.text(m+1,eps+0.01,(m,a),color='r') #标注出拐点及其坐标
plt.scatter(m,eps,color="r", label='拐点')
plt.plot([-5,m],[eps,eps],linestyle="--",color = "r")
plt.plot([m,m],[-5,eps],linestyle="--",color = "r")
plt.legend(loc='upper right') #添加图例
# 给拐点添加注释
# plt.annotate(r"eps= 0.018",xy=(m,eps),color = "r",xycoords='data',xytext=(+10,0),
#                  textcoords='offset points')


# 设置坐标范围

x_major_locator=MultipleLocator(20)
#把x轴的主刻度间隔设置为10，并存在变量里
y_major_locator=MultipleLocator(.1)
#把y轴的主刻度间隔设置为0.02，并存在变量里
x_minorLocator = MultipleLocator(10) #将x轴次刻度标签设置为10的倍数
y_minorLocator = MultipleLocator(.05) #将此y轴次刻度标签设置为0.01的倍数
ax=plt.gca()
#ax为两条坐标轴的实例
ax.xaxis.set_major_locator(x_major_locator)
#把x轴的主刻度设置为1的倍数
ax.yaxis.set_major_locator(y_major_locator)
#设置次刻度标签的位置,没有标签文本格式
ax.xaxis.set_minor_locator(x_minorLocator)
ax.yaxis.set_minor_locator(y_minorLocator)
#把xy轴的刻度间隔设置为1，并存在变量里
plt.ylim(-0.005, 0.2)  # 设置x轴范围
plt.xlim(-5, 40)  # 设置y轴范围


plt.xlabel('目标序列',)             #设置x，y轴的标签
plt.ylabel('Eps')
plt.savefig(index_number, dpi=100, bbox_inches='tight', pad_inches=0.2)
# plt.show()

#输出聚类效果评价参数
Dbscan_result = dbscan_cluster(data_norm,eps)



