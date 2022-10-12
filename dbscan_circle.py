import gdal
import numpy as np
import os
import numpy as np
import pandas as pd

from sklearn.cluster import DBSCAN
from sklearn.cluster import OPTICS
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
	dbscan_result =DBSCAN(eps=eps,min_samples=4).fit_predict(data_norm)
	matrix = np.zeros((data_x, data_y)) #初始化0矩阵,之后可以加你想要的值
	matrix = matrix+200
	for i in range(kmeans_xy.shape[0]):
		matrix[kmeans_xy[i][0]][kmeans_xy[i][1]] = dbscan_result[i]
	# Optics_result =OPTICS(min_samples=3+1).fit(data_norm)
	# print("result matrix",np.max(matrix))
	return matrix


def start_gdal(path):
	print("start gdal")
	raster_file = 'H:/basicData/MCD64A1_output/DXAL_mcd64a1/Jenks/db_result'+''+str(path)  # 输出的栅格文件路径
	src_ras_file = "H:/basicData/MCD64A1_output/DXAL_mcd64a1/dxal_MCD64A1_2002_Clip1.tif"  # 提供地理坐标信息和几何信息的栅格底图
	dataset = gdal.Open(src_ras_file)
	projection = dataset.GetProjection()
	transform = dataset.GetGeoTransform()

	arr2raster(Dbscan_result, raster_file, prj=projection, trans=transform)

# TODO
index_number = 0
#写入文件夹目录下的每幅影像对应的参数list
eps_list=[0.031,0.018,0.006,
          0.065,0.047,0.046,
          0.049,0.047,0.035,
          0.025,0.013,0.026,
          0.025,0.024,0.019,
          0.037,0.030,0.015,
          0.018,0.061,0.044,
          0.066,0.060,0.032,
          0.016,0.007,
          0.071,0.029,0.030,
          0.007,0.100,0.032,
          0.067,0.023,
          0.022,0.046,
          0.036,0.015,0.018,
          0.036,0.057,
          0.039,0.012,
          0.082,0.010,0.030,
          0.044,0.007,0.063,
          0.009,0.005,
          0.047,0.042]
number = len(eps_list)
path = "H:/basicData/MCD64A1_output/DXAL_mcd64a1/Jenks/"  # 设置路径
dirs = os.listdir(path)                    # 获取指定路径下的文件
for tif_index in dirs:                             # 循环读取路径下的文件并筛选输出
	if os.path.splitext(tif_index)[1] == ".tif":
		tif_path = "H:/basicData/MCD64A1_output/DXAL_mcd64a1/Jenks/"+str(tif_index)
		dataset = gdal.Open(tif_path)
		print("tif_path is ", tif_path)
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






