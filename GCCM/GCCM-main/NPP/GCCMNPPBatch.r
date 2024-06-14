setwd("D:\\wxy_files\\paper_model\\GCCM\\GCCM-main")


library(parallel)
library(foreach)
library(doParallel)
library(sf)
library(stars)

#source("D:\\wxy_files\\paper_model\\GCCM\\GCCM-main\\NPP\\GCCMNPPBatch.r")
source("D:\\wxy_files\\paper_model\\GCCM\\GCCM-main\\NPP\\GCCMParal.r")

load("D:\\wxy_files\\paper_model\\GCCM\\GCCM-main\\NPP\\npp.RData")     #load the data, the data can be prepared with following code

#####################npp#################
npp <- read_stars("D:\\wxy_files\\paper_model\\GCCM\\GCCM-main\\NPP\\npp10km.tif")
nppImage<-as.matrix(npp)

climates<-c("pre10km","tem10km1")

climateImages<-list()
for(e in seq(1:length(climates)))
{
  fileName<-paste("D:\\wxy_files\\paper_model\\GCCM\\GCCM-main\\NPP\\",climates[e],".tif",sep = "")
  climateImages[[e]]<-as.matrix(read_stars(fileName))
}

save(nppImage,climateImages,file="D:\\wxy_files\\paper_model\\GCCM\\GCCM-main\\NPP\\npp.RData")




xNames<-c("pre10km","tem10km1") #""

yName<-"NPP"


yMatrix<-nppImage



lib_sizes<-seq(20,300,20)  # library sizes, will be the horizontal ordinate  of the reulst plot.Note here the lib_size is the window size
                           # The largest value ('to' parameter) can be set to the largest size of immage (the minor of width and length)
                           # the 'by' can be set by takning accout to the computation time

E<-3             # the dimensions of the embedings   
lib<-NULL

imageSize<-dim(yMatrix)   
totalRow<-imageSize[1]     #Get the row number of image
totalCol<-imageSize[2]     #Get the collumn number of image
predRows<-seq(10,totalRow,10)
predCols<-seq(10,totalCol,10)   #To save the computation time, not every pixels are predict. The results are almost the same due to the spatial autocorrealtion 





#If computation resources are enough, this filter can be ignored

pred<-merge(predRows,predCols)

#plot(yImage)
coodsX<-seq(1,totalRow)
coodsY<-seq(1,totalCol)

coords<-merge(coodsX,coodsY)

colnames(coords)<-c("coordX","coordY")

y<-as.vector(yMatrix)

lmModel<-lm(y ~ coordX+coordY, cbind(y,coords))  #remove the linear trend of y
prediction<-predict(lmModel,coords)
y<-y-prediction


yMatrixM<-matrix(y,nrow = totalRow, ncol = totalCol)

for(c in seq(1:length(climateImages)))
{
  
  xMatrix<- climateImages[[c]]
  
  x<-as.vector(xMatrix)
  
  lmModel<-lm(x ~ coordX+coordY, cbind(x,coords))    #remove the linear trend of x 
  prediction<-predict(lmModel,coords)
  x<-x-prediction
  xMatrixM<-matrix(x,nrow = totalRow, ncol = totalCol)
  
  
  startTime<-Sys.time()
  
  if(c==2)
  {
    E=5
  }
  
  x_xmap_y <- GCCM(xMatrixM, yMatrixM, lib_sizes, lib, pred, E,cores=32) # predict y with x
  y_xmap_x <- GCCM(yMatrixM, xMatrixM, lib_sizes, lib, pred, E,cores=32) #predict x with y
  
  endTime<-Sys.time()
  
  print(difftime(endTime,startTime, units ="mins"))
  
  x_xmap_y$L <- as.factor(x_xmap_y$L)
  x_xmap_y_means <- do.call(rbind, lapply(split(x_xmap_y, x_xmap_y$L), function(x){max(0, mean(x$rho,na.rm=TRUE))}))
  #calculate the mean of prediction accuray, measure by Pearson correlation
  
  y_xmap_x$L <- as.factor(y_xmap_x$L)
  y_xmap_x_means <- do.call(rbind, lapply(split(y_xmap_x, y_xmap_x$L), function(x){max(0, mean(x$rho,na.rm=TRUE))}))
  #calculate the mean of prediction accuray, measure by Pearson correlation
  
  
  predIndices<-locate(pred[,1],pred[,2],totalRow,totalCol)
  yPred<- as.array(t(yMatrix))
  predicted<-na.omit(yPred[predIndices])
  
  x_xmap_y_Sig<- significance(x_xmap_y_means,length(predicted))    #Test the significance of the prediciton accuray
  y_xmap_x_Sig<- significance(y_xmap_x_means,length(predicted))     #Test the significance of the prediciton accuray
  
  
  x_xmap_y_interval<- confidence(x_xmap_y_means,length(predicted)) #calculate the  95%. confidence interval  of the prediciton accuray
  colnames(x_xmap_y_interval)<-c("x_xmap_y_upper","x_xmap_y_lower")
  
  y_xmap_x_interval<- confidence(y_xmap_x_means,length(predicted)) #calculate the  95%. confidence interval  of the prediciton accuray
  colnames(y_xmap_x_interval)<-c("y_xmap_x_upper","y_xmap_x_lower")
  
  results<-data.frame(lib_sizes,x_xmap_y_means,y_xmap_x_means,x_xmap_y_Sig,y_xmap_x_Sig,x_xmap_y_interval,y_xmap_x_interval) #Save the cross-mapping prediciton results
  
  write.csv(results,file=paste("results/NPP/",xName,"_",yName,"_Pral.csv",sep=""))
  
  par(mfrow=c(1,1))
  par(mar=c(5, 4, 4, 2) + 0.1)
  
  jpeg(filename = paste("results/NPP/",xName,"_",yName,"_Pral.jpg",sep = ""),width = 600, height = 400)    #Plot the cross-mapping prediciton results
  
  plot(lib_sizes, x_xmap_y_means, type = "l", col = "royalblue", lwd = 2,
       xlim = c(min(lib_sizes), max(lib_sizes)), ylim = c(0.0, 1), xlab = "L", ylab = expression(rho))
  lines(lib_sizes, y_xmap_x_means, col = "red3", lwd = 2)
  legend(min(lib_sizes), 1, legend = c("x xmap y", "y xmap x"), 
         xjust = 0, yjust = 1, lty = 1, lwd = 2, col = c("royalblue", "red3"))
  
  dev.off()
  
}





