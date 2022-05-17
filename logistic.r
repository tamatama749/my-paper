#对数据进行分层抽样
library(sampling)

firedata<-read.csv("alldata.csv")
dim(firedata)
str(firedata)

set.seed(12345)
index <-  sort(sample(nrow(firedata), nrow(firedata)*.7))
train <- firedata[index,]
test <-  firedata[-index,]


model<-glm(FIRE~.,data=train,family = "binomial")

summary(model)

#使用逐步回归法进行变量的选择 
model2<-step(object = model,trace = 0)
summary(model2)
#变量的P值均小于0.05，通过显著性检验，保留了相对重要的变量。
#模型各变量通过显著性检验的同时还需确保整个模型是显著的。
#模型的卡方检验
anova(object = model2,test = "Chisq")

#测试数据的检验
prob<-predict(object =model2,newdata=test,type = "response")
pred<-ifelse(prob>=0.5,"yes","no")
pred<-factor(pred,levels = c("no","yes"),order=TRUE)
f<-table(test$FIRE,pred)
f

#绘制ROC曲线
install.packages("pROC")
library(pROC)

roc_curve <- roc(test$FIRE,prob)
names(roc_curve)
auc <- round(auc(test$FIRE,prob),4)
x <- 1-roc_curve$specificities
y <- roc_curve$sensitivities

library(ggplot2)
p <- ggplot(data = NULL, mapping = aes(x= x, y = y))+
  geom_line(colour = 'red') +geom_abline(intercept = 0, slope = 1)+
  annotate('text', x = 0.4, y = 0.5, label = paste('AUC=',round(roc_curve$auc,2)))+
  labs(x = '1-specificities',y = 'sensitivities', title = 'ROC Curve')

p2 <- ggroc(roc_curve, color = "red",linetype = 1,size = 1,alpha = 1,legacy.axes = T)+ 
  geom_abline(intercept = 0, slope = 1, color="grey", size = 1, linetype=1)+ 
  labs(x = "False Positive Rate (1-Specificity)", y= "True Positive Rate (Sensivity or Recall)")+ 
  annotate("text",x = .75, y= .25, label=paste("AUC =", auc),
           size = 5, family="serif")+ 
  coord_cartesian(xlim =c(0, 1), ylim =c(0, 1))+
  theme_bw()+
  theme (panel.background = element_rect(fill = 'transparent'), 
                    axis.ticks.length = unit(0.4, "lines"), 
                    axis.ticks = element_line(color='black'),
                    axis.line = element_line(size=.5, colour = "black"),
                    axis.title = element_text (colour=' black', size=12, face = "bold"), 
                    axis.text = element_text(colour=' black' , size=10, face = "bold"), 
                    text = element_text(size=8, color="black", family="serif"))
