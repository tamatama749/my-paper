import gdal
import numpy as np
import os
import numpy as np
import pandas as pd

from sklearn.cluster import DBSCAN
from sklearn.cluster import OPTICS
from sklearn.cluster import KMeans
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
#建立聚类模型
def dbscan_cluster(data_norm,eps):
	print("start dbscan")
	print("eps_number",eps)
	dbscan_result =DBSCAN(eps=eps,min_samples=3+1).fit_predict(data_norm)
	matrix = np.zeros((data_x, data_y)) #初始化0矩阵,之后可以加你想要的值
	matrix = matrix+200
	for i in range(kmeans_xy.shape[0]):
		matrix[kmeans_xy[i][0]][kmeans_xy[i][1]] = dbscan_result[i]
	# Optics_result =OPTICS(min_samples=3).fit(data_norm)
	# print("result matrix",np.max(matrix))
	return matrix

#kmeans方法
# def kmeans__cluster(data_norm):
# 	kmeans_predict = KMeans(n_clusters=50).fit_predict(data_norm)
# 	matrix = np.zeros((data_x,data_y))
#     matrix = matrix+200
# 	for i in range(kmeans_xy.shape[0]):
# 		matrix[kmeans_xy[i][0]][kmeans_xy[i][1]]=kmeans_predict[i]
# 	return matrix

def start_gdal(path):
	print("start gdal")
	raster_file = 'H:/basicData/MCD64A1_output/DXAL_mcd64a1/dbscan_output'+'dbscan_result'+str(path)  # 输出的栅格文件路径
	src_ras_file = "H:/basicData/MCD64A1_output/DXAL_mcd64a1/dxal_MCD64A1_2002_Clip1.tif"  # 提供地理坐标信息和几何信息的栅格底图
	dataset = gdal.Open(src_ras_file)
	projection = dataset.GetProjection()
	transform = dataset.GetGeoTransform()

	arr2raster(Dbscan_result, raster_file, prj=projection, trans=transform)

# TODO
index_number = 0
eps_list=[0.06,0.12,0.2,0.09,0.14,0.22,0.23,0.15,0.05,0.1,0.18,0.09,0.01,0.16,0.08,0.23,0.25,0.1]
number = len(eps_list)
path = "H:/basicData/MCD64A1_output/DXAL_mcd64a1/"  # 设置路径
dirs = os.listdir(path)                    # 获取指定路径下的文件
for tif_index in dirs:                             # 循环读取路径下的文件并筛选输出
	if os.path.splitext(tif_index)[1] == ".tif":
		tif_path = "H:/basicData/MCD64A1_output/DXAL_mcd64a1/"+str(tif_index)
		dataset = gdal.Open(tif_path)
		print(tif_path)
		XSize = dataset.RasterXSize  # 网格的X轴像素数量
		YSize = dataset.RasterYSize  # 网格的Y轴像素数量
		im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
		im_proj = dataset.GetProjection()  # 地图投影信息
		data = dataset.ReadAsArray(0, 0, XSize, YSize).astype(np.float32)
		data_x = data.shape[0]
		data_y = data.shape[1]
		data_days = data.ravel()[np.flatnonzero(data)]
		kmeans_xy = np.nonzero(data)
		kmeans_xy = np.array(kmeans_xy)
		kmeans_xy = kmeans_xy.T
		kmeans_xyd = np.insert(kmeans_xy, 2, data_days, 1)
		print(kmeans_xyd.shape)
		data_norm = normalize(kmeans_xyd, axis=0, norm='max')
		Dbscan_result = dbscan_cluster(data_norm,eps_list[index_number])
		start_gdal(tif_index)
		index_number = index_number+1

# data_norm=normalize(kmeans_xyd,axis=2,norm='max')
# dataset = gdal.Open("H:/basicData/MCD64A1_output/DXAL_mcd64a1/dxal_MCD64A1_2000_Clip1.tif")
# BBand = dataset.GetRasterBand(band)






#Dbscan方法
#方法一：eps参数选取
# import matplotlib.pyplot as plt;
# def select_MinPts(data_norm,k):
#     k_dist = []
#     for i in range(data_norm.shape[0]):
#         dist = (((data_norm[i] - data_norm)**2).sum(axis=1)**0.5)
#         dist.sort()
#         k_dist.append(dist[k])
#     return np.array(k_dist)
# k = 3  # 此处k取 2*维度 -1，维度为特征数
# k_dist = select_MinPts(data_norm,k)
# k_dist.sort()
# plt.plot(np.arange(k_dist.shape[0]),k_dist[::-1])
# eps = k_dist[::-1][15]
# plt.scatter(15,eps,color="r")
# plt.plot([0,15],[eps,eps],linestyle="--",color = "r")
# plt.plot([15,15],[0,eps],linestyle="--",color = "r")
#
# plt.show()

# 方法二：迭代不同值的参数
# 构建空列表，用于保存不同参数组合下的结果
res = []
# 迭代不同的eps值
for eps in np.arange(0.001,1,0.05):
    # 迭代不同的min_samples值
    for min_samples in range(2,10):
        dbscan = DBSCAN(eps = eps, min_samples = min_samples)
        # 模型拟合
        dbscan.fit(data_norm)
        # 统计各参数组合下的聚类个数（-1表示异常点）
        n_clusters = len([i for i in set(dbscan.labels_) if i != -1])
        # 异常点的个数
        outliners = np.sum(np.where(dbscan.labels_ == -1, 1,0))
        # 统计每个簇的样本个数
        stats = str(pd.Series([i for i in dbscan.labels_ if i != -1]).value_counts().values)
        res.append({'eps':eps,'min_samples':min_samples,'n_clusters':n_clusters,'outliners':outliners,'stats':stats})
# 将迭代后的结果存储到数据框中
df = pd.DataFrame(res)

# 根据条件筛选合理的参数组合
df.loc[df.n_clusters == 3, :]






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

