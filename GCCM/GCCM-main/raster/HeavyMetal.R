setwd("E:\\Study\\R\\spatial-causality")
setwd("C:\\Users\\suhui\\Documents\\马伟波-论文复现\\GCCM\\GCCM-main\\Synthetic")
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


xImage<-readGDAL("dTRI.tif")     #read the casue variable 
yImage<-readGDAL("Cu.tif")       #read the effect variable 
 
plot(xImage)                   #plot the casue variable 
plot(yImage)                   #plot the casue variable 

xMatrix<-as.matrix(xImage)
yMatrix<-as.matrix(yImage)


lib_sizes<-seq(10,120,20)   # library sizes, will be the horizontal ordinate  of the reulst plot.Note here the lib_size is the window size
                            # The largest value ('to' parameter) can be set to the largest size of immage (the minor of width and length)
                            # the 'by' can be set by taking account to the computation time

E<-3                           # the dimensions of the embeddings   
lib<-NULL
# pred<-

imageSize<-dim(xMatrix)
totalRow<-imageSize[1]        #Get the row number of image
totalCol<-imageSize[2]         #Get the collumn number of image
predRows<-seq(5,totalRow,5)    #To save the computation time, not every pixels are predict. The results are almost the same due to the spatial autocorrealtion 
                               #If computation resources are enough, this filter can be ignored 
predCols<-seq(5,totalCol,5)

pred<-merge(predRows,predCols)

startTime<-Sys.time()

x_xmap_y <- GCCM(xMatrix, yMatrix, lib_sizes, lib, pred, E,cores=8)   #predict y with x
y_xmap_x <- GCCM(yMatrix,xMatrix, lib_sizes, lib, pred, E,cores=8)    #predict x with y

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

results<-data.frame(lib_sizes,x_xmap_y_means,y_xmap_x_means,x_xmap_y_Sig,y_xmap_x_Sig,x_xmap_y_interval,y_xmap_x_interval)  #Save the cross-mapping prediciton results


write.csv(results,file="result_dTRI_nlights03.csv")     

par(mfrow=c(1,1))
par(mar=c(5, 4, 4, 2) + 0.1)

jpeg(filename = "Result_dTRI_nlights03.jpg",width = 600, height = 400)     #Plot the cross-mapping prediciton results
plot(lib_sizes, x_xmap_y_means, type = "l", col = "royalblue", lwd = 2, 
     xlim = c(min(lib_sizes), max(lib_sizes)), ylim = c(0.0, 1), xlab = "L", ylab = expression(rho))
lines(lib_sizes, y_xmap_x_means, col = "red3", lwd = 2)
legend(min(lib_sizes), 1, legend = c("x xmap y", "y xmap x"), 
       xjust = 0, yjust = 1, lty = 1, lwd = 2, col = c("royalblue", "red3"))
dev.off()
