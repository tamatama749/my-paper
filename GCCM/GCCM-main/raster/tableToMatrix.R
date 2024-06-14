# install.packages("readr")
library(readr)
library(raster)
library(GSIF)
library(rgdal)
library(raster)
library(gstat)
library(ranger)
library(scales)
library(sp)
library(lattice)
library(gridExtra)
library(intamap)
library(maxlike)
library(spatstat)
library(entropy)
library(gdistance)
library(DescTools)

library(parallel)
library(foreach)
library(doParallel)

source("basic.r")
source("GCCM.r")
#读取GIS重采样后的栅格文件生成矩阵
#raster_data <- raster("C:\\Users\\suhui\\Documents\\马伟波-论文复现\\data\\CITYraster_02.tif")
#target_raster <- raster(nrows=35, ncols=37, 
#                        xmn=extent(raster_data)[1], xmx=extent(raster_data)[2], 
#                        ymn=extent(raster_data)[3], ymx=extent(raster_data)[4])
#resampled_raster <- resample(raster_data, target_raster, method="bilinear")
#raster_matrix <- as.matrix(raster_data)
#print(raster_matrix)
#
#raster_matrix[raster_matrix == 1] <- 6.9547

# 读取CSV文件
file_path <- "C:\\Users\\suhui\\Documents\\马伟波-论文复现\\data\\逐年统计数据.csv"
data <- read_csv(file_path)

# 获取列名
column_names <- colnames(data)

# 排除“城市”和“编号”列
variable_names <- setdiff(column_names, c("城市", "编号"))
# 排除变量名中的年份和单位信息
variable_names_no_year <- gsub("20[0-9]{2}年", "", variable_names)
variable_names_no_year <- gsub("\\（.*?\\）", "", variable_names_no_year)
variable_names_no_year <- unique(variable_names_no_year)
# 打印变量名称
print(variable_names_no_year)

# 打印列名以确认所需列名
#print(colnames(data))

# 假设要读取的目标变量
target_column1 <- "2020年碳排放量（百万吨）"
target_column2<- "2020年工业废水排放效率（万吨/亿元）"
year<-substr(target_column1, 1, 5)
target_x <- gsub("\\（.*?\\）", "", target_column1)
target_x <- gsub("20[0-9]{2}年", "", target_x)
target_y <- gsub("\\（.*?\\）", "", target_column2)
target_y <- gsub("20[0-9]{2}年", "", target_y)
# 获取城市名和对应的值
city_values1 <- data[, c("城市", target_column1)]
city_values2 <- data[, c("城市", target_column2)]

# 定义城市在矩阵中的位置
city_positions <- list(
  "安庆" = c(4, 1),"合肥" = c(3, 2), "铜陵" = c(4, 2),"池州" = c(5, 2), 
  "滁州" = c(2, 3), "马鞍山" = c(3, 3), "芜湖" = c(4, 3),
  "扬州" = c(2, 4), "镇江" = c(3, 4), "南京" = c(4, 4), "宣城" = c(5, 4),  
  "盐城" = c(1, 5), "泰州" = c(2, 5), "常州" = c(3, 5), "无锡" = c(4, 5),"湖州" = c(5, 5), "杭州" = c(6, 5),"金华" = c(7, 5),
  "南通" = c(3, 6),   "苏州" = c(4, 6), "嘉兴" = c(5, 6), "绍兴" = c(6, 6), "台州" = c(7, 6),  "温州" = c(8, 6),
  "上海" = c(4, 7), "宁波" = c(6, 7), 
  "舟山" = c(6, 8)
)

#定义一个矩阵
city_xMatrix <- matrix(NA, nrow = 8, ncol = 8)
city_yMatrix <- matrix(NA, nrow = 8, ncol = 8)
# 遍历城市并将对应的值赋给矩阵中的相应位置
for (i in 1:nrow(city_values1)) {
  city <- city_values1$城市[i]
  value <- city_values1[[target_column1]][i]
  if (city %in% names(city_positions)) {
    pos <- city_positions[[city]]
    city_xMatrix[pos[1], pos[2]] <- value
  }
}


for (i in 1:nrow(city_values2)) {
  city <- city_values2$城市[i]
  value <- city_values2[[target_column2]][i]
  if (city %in% names(city_positions)) {
    pos <- city_positions[[city]]
    city_yMatrix[pos[1], pos[2]] <- value
  }
}
city_xMatrix[is.na (city_xMatrix)] <- 0
city_yMatrix[is.na (city_yMatrix)] <- 0


#开始因果分析
lib_sizes<-seq(2,8,1)   #这是库大小的列表，即滑动窗口的大小。此值从 2 到 8 按加1递增。
# library sizes, will be the horizontal ordinate  of the reulst plot.Note here the lib_size is the window size
# The largest value ('to' parameter) can be set to the largest size of immage (the minor of width and length)
# the 'by' can be set by taking account to the computation time

E<-3                           # the dimensions of the embeddings   
lib<-NULL

imageSize<-dim(city_xMatrix)
totalRow<-imageSize[1]        #Get the row number of image
totalCol<-imageSize[2]         #Get the collumn number of image
predRows<-seq(2,totalRow,1)    #To save the computation time, not every pixels are predict. The results are almost the same due to the spatial autocorrealtion 
#If computation resources are enough, this filter can be ignored 
predCols<-seq(2,totalCol,1)

pred<-merge(predRows,predCols)


startTime<-Sys.time()

x_xmap_y <- GCCM(city_xMatrix, city_yMatrix, lib_sizes, lib, pred, E,cores=8)   #predict y with x
y_xmap_x <- GCCM(city_yMatrix,city_xMatrix, lib_sizes, lib, pred, E,cores=8)    #predict x with y

endTime<-Sys.time()

print(difftime(endTime,startTime, units ="mins"))

x_xmap_y$L <- as.factor(x_xmap_y$L)
x_xmap_y_means <- do.call(rbind, lapply(split(x_xmap_y, x_xmap_y$L), function(x){max(0, mean(x$rho,na.rm=TRUE))}))
#calculate the mean of prediction accuray, measure by Pearson correlation


y_xmap_x$L <- as.factor(y_xmap_x$L)
y_xmap_x_means <- do.call(rbind, lapply(split(y_xmap_x, y_xmap_x$L), function(x){max(0, mean(x$rho,na.rm=TRUE))}))
#calculate the mean of prediction accuray, measure by Pearson correlation

x_xmap_y_Sig<- significance(x_xmap_y_means,nrow(pred))    #Test the significance of the prediciton accuray
y_xmap_x_Sig<- significance(y_xmap_x_means,nrow(pred))     #Test the significance of the prediciton accuray

x_xmap_y_interval<- confidence(x_xmap_y_means,nrow(pred))
colnames(x_xmap_y_interval)<-c("x_xmap_y_upper","x_xmap_y_lower")   #calculate the  95%. confidence interval  of the prediciton accuray

y_xmap_x_interval<- confidence(y_xmap_x_means,nrow(pred))
colnames(y_xmap_x_interval)<-c("y_xmap_x_upper","y_xmap_x_lower")  #calculate the  95%. confidence interval  of the prediciton accuray

csv_filename <- paste0(year, "_x_", target_x, "_y_", target_y, ".csv")
results<-data.frame(lib_sizes,x_xmap_y_means,y_xmap_x_means,x_xmap_y_Sig,y_xmap_x_Sig,x_xmap_y_interval,y_xmap_x_interval)  #Save the cross-mapping prediciton results

# 定义输出目录
setwd("C:/Users/suhui/Documents/马伟波-论文复现/GCCM/GCCM-main/Synthetic/results/") 
write.csv(results,file=csv_filename)     

# 动态生成图例
legend_text <- c(paste(target_x," xmap ", target_y, sep = ""), paste(target_y," xmap ", target_x, sep = ""))

jpg_filename <- paste0("Result_",year,target_x,"_",target_y,".jpg")
jpeg(filename = jpg_filename, width = 600, height = 400)     #Plot the cross-mapping prediciton results
plot(lib_sizes, x_xmap_y_means, type = "l", col = "royalblue", lwd = 2, 
     xlim = c(min(lib_sizes), max(lib_sizes)), ylim = c(0.0, 1), xlab = "L", ylab = expression(rho))

lines(lib_sizes, y_xmap_x_means, col = "red3", lwd = 2)
legend(min(lib_sizes), 1, legend = legend_text, 
       xjust = 0, yjust = 1, lty = 1, lwd = 2, col = c("royalblue", "red3"))
title(year)
dev.off()


