#打开Rstudio，安装所需package，并在运行前勾选上
install.packages("Randomforest")
library(Randomforest) 
install.packages("raster")
library(raster) 

#设置工作空间
setwd("H:/wjrdata/build/test/Stratified") 
#biomass22：变量名，可以自己定义，此句为读取csv（csv里有一列为biomass其余列为遥感影像光谱特征变换的值）
biomass22<- read.csv("1992_dd.csv") 

#将数据随机分以80%与20%为两组，80%为训练数据，20%为验证数据
ind<-sample(2,nrow(biomass22),replace=TRUE,prob=c(0.8,0.2))
#将训练数据与验证数据写到新的csv里，此步骤只需运行一次，重复运行会改变分组
traindata<- biomass22 [ind==1,]
testdata<- biomass22 [ind==2,] 

#在第一遍选择重要性变量时这句可省略，选择完重要性变量后再运行
write.csv(traindata, file="1992_train.csv")
write.csv(testdata, file="1992_test.csv") 

traindata<-read.csv("1992_train.csv")
testdata<-read.csv("1992_test.csv")

#处理表格空值
biomass22=na.omit(biomass22)

names(traindata) <- gsub("_", "", names(traindata)) #检查数据是否有缺失值
summary(traindata)
traindata[traindata == ""] <- NA  #用NA代替所有的空白
traindata <- traindata[complete.cases(traindata),]        #处理缺失值，即成列删除


#建模效果的展示,选择重要性变量
rf<- randomForest(biomass~.-ID-X-Y-Map_x-Map_y-Lat-Lon, data=biomass22, importance = TRUE, mtry=1, do.trace=100, ntree =300, oob.prox = TRUE, nodesize=5) #随机森林核心语句，biomass为因变量，-ID为减去不需要的自变量，mtry，ntree等参数可以调整以改进建模结果 data为参与的csv
print(rf) 
importance(rf) #查看模型自变量的重要性，值越大，越重要。第一遍运行到此结束
varImpPlot(rf)
#结束第一次运行之后，选择重要性较高的自变量，在训练数据中将其余自变量删掉开始第二次运行


#读取训练数据
density<- read.csv("1992_train.csv")
#随机森林建模
rf<- randomForest(biomass~.-样地号-Lon-Lat, data=density, importance = TRUE, mtry=1, do.trace=100, ntree =300, oob.prox = TRUE, nodesize=5)
#预测训练结果
predict(rf, density)
output1<-predict(rf, density)
plot(predict(rf), density$biomass)
abline(lm(traindata$biomass~predict(rf)))
#将训练结果写入新的csv中，与biomass实测值建立散点图，看R2
write.csv(output1, file = "result_92train.csv")
#预测验证数据
predict(rf, testdata)
output2<-predict(rf, testdata)
#将验证结果写入新的csv中，与biomass实测值建立散点图，看R2，计算平均相对误差
write.csv(output2, file = "result_92test.csv")

#生物量制图，将所需要的变量layerstacking的图读取
whole_bands=brick("H:/wjrdata/build/test/Stratified/92layer/layer1992")
whole_bands1 <- approxNA(whole_bands)

#定义波段名称，变量顺序需要与envi里堆栈后影像图层保持一致，变量名与rf模型因变量一致
names(whole_bands1)=c("SAVI", "VRI", "b2","b5","b7","tm14","tm17","tm37","second77","tm7_1")
#用rf预测全局生物量，并输出
img_bio <- predict(whole_bands1, rf, type="response")
writeRaster(img_bio,"try", format="ENVI", datatype="FLT4S", overwrite=TRUE)