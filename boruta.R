#安装并且调用boruta包
install.packages("Boruta")
library(Boruta) 

setwd("H:/wjrdata/build/test/boruta")  #设定工作空间，这句也可以直接与下一句合并
traindata <- read.csv("1988_train.csv", header = T, stringsAsFactors = F)

#检查数据是否有缺失值
str(traindata)
names(traindata) <- gsub("_", "", names(traindata)) 
summary(traindata)
#用NA代替所有的空白
traindata[traindata == ""] <- NA 
#处理缺失值，即成列删除
traindata <- traindata[complete.cases(traindata),]    

#将分类变量转换为因子数据类型
convert <- c(2:6, 11:13)
traindata[,convert] <- data.frame(apply(traindata[convert], 2, as.factor))   

#实施和检查Boruta包的性能，几个被拒绝，几个被确认，几个属性被指定为暂定。暂定属性的重要性非常接近最好的阴影属性，以至于Boruta无法对随机森林运行的默认数量作出有强烈信心的判定
set.seed(123)
boruta.train <- Boruta(biomass~.-row.names, data = traindata, doTrace = 2)
print(boruta.train)

#用图表展示Boruta变量的重要性，默认情况下，由于缺乏空间，Boruta绘图功能添加属性值到横的X轴会导致所有的属性值都无法显示。在这里把属性添加到直立的X轴。红色、黄色和绿色的盒状图分别代表拒绝、暂定和确认属性的Z分数
plot(boruta.train, xlab = "", xaxt = "n")
lz<-lapply(1:ncol(boruta.train$ImpHistory),function(i)+boruta.train$ImpHistory[is.finite(boruta.train$ImpHistory[,i]),i])
names(lz) <- colnames(boruta.train$ImpHistory)
Labels <- sort(sapply(lz,median))
axis(side = 1,las=2,labels = names(Labels),at = 1:ncol(boruta.train$ImpHistory), cex.axis = 0.7)

#对实验性属性进行判定。实验性属性将通过比较属性的Z分数中位数和最佳阴影属性的Z分数中位数被归类为确认或拒绝
final.boruta <- TentativeRoughFix(boruta.train)
print(final.boruta)

#获取确认属性的列表
getSelectedAttributes(final.boruta, withTentative = F)
#创建一个来自Boruta最终结果的数据框架
boruta.df <- attStats(final.boruta)
class(boruta.df)
print(boruta.df)
#输出数据表
write.csv(boruta.df, file = "1988_train.csv")