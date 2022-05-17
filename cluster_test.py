import gdal
import numpy as np
import os
import numpy as np
from dbscan import dbscan
from sklearn.cluster import DBSCAN
from sklearn.cluster import OPTICS
from sklearn.cluster import KMeans
from spectral_clustering import chose_para
from sklearn.datasets import make_classification
from sklearn.mixture import GaussianMixture
from numpy import unique
from numpy import where
from matplotlib import pyplot
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


dataset = gdal.Open("H:/basicData/MCD64A1_output/DXAL_mcd64a1/dxal_MCD64A1_2000_Clip1.tif")
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

# #kmeans方法
# def kmeans__cluster(data_norm):
# 	kmeans_predict = KMeans(n_clusters=50).fit_predict(data_norm)
# 	matrix = np.zeros((data_x,data_y))
#   matrix = matrix+200
# 	for i in range(kmeans_xy.shape[0]):
# 		matrix[kmeans_xy[i][0]][kmeans_xy[i][1]]=kmeans_predict[i]
# 	return matrix


#Dbscan方法
#eps参数选取
import matplotlib.pyplot as plt;
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
plt.plot(np.arange(k_dist.shape[0]),k_dist[::-1])
eps = k_dist[::-1][15]
plt.scatter(15,eps,color="r")
plt.plot([0,15],[eps,eps],linestyle="--",color = "r")
plt.plot([15,15],[0,eps],linestyle="--",color = "r")

plt.show()
#建立聚类模型
# def dbscan_cluster(data_norm):
# 	print("start dbscan")
# 	dbscan_result =DBSCAN(eps=0.1,min_samples=k+1).fit_predict(data_norm)
# 	matrix = np.zeros((data_x, data_y)) #初始化0矩阵,之后可以加你想要的值
# 	matrix = matrix+200
# 	for i in range(kmeans_xy.shape[0]):
# 		matrix[kmeans_xy[i][0]][kmeans_xy[i][1]] = dbscan_result[i]
# 	# Optics_result =OPTICS(min_samples=3).fit(data_norm)
# 	# print("result matrix",np.max(matrix))
# 	return matrix

# # GMM方法
# def GMM_cluster(data_norm):
# 	model = GaussianMixture(n_components=10)
# 	model.fit(data_norm)
# 	yhat = model.predict(data_norm)
# 	matrix = np.zeros((data_x, data_y))
#   matrix = matrix + 200
# 	for i in range(kmeans_xy.shape[0]):
# 		matrix[kmeans_xy[i][0]][kmeans_xy[i][1]] = yhat[i]
# 	return metrix


# kmeans_result = kmeans__cluster(data_norm)
# Dbscan_result = dbscan_cluster(data_norm)
# GMM_result = GMM_cluster(data_norm)

# print("start gdal")
# raster_file = 'H:/basicData/MCD64A1_output/DXAL_mcd64a1/dbscan_Rastercalc12.tif'  # 输出的栅格文件路径
# src_ras_file = "H:/basicData/MCD64A1_output/DXAL_mcd64a1/dxal_MCD64A1_2002_Clip1.tif"  # 提供地理坐标信息和几何信息的栅格底图
# dataset = gdal.Open(src_ras_file)
# projection = dataset.GetProjection()
# transform = dataset.GetGeoTransform()
#
# arr2raster(Dbscan_result, raster_file, prj=projection, trans=transform)
