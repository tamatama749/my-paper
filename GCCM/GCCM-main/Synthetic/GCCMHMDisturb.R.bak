setwd("E:\\Study\\R\\spatial-causality")


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


set.seed(2023)

lib_sizes<-seq(10,120,20)
E<-3
lib<-NULL

HMs<-c("Cu","Pb","Cd","Mg")

Envs<-c("dTRI","nlights03")

sink("results/HMSim/process.txt")

for(h in seq(1:length(HMs)))
{
  yName<-HMs[h]
  
  yImage<-readGDAL(paste(yName,".tif",sep = ""))
  
  yMatrix<-as.matrix(yImage)

  #y<-as.vector(yMatrix)
  
  imageSize<-dim(yMatrix)
  totalRow<-imageSize[1]
  totalCol<-imageSize[2]
  predRows<-seq(5,totalRow,5)
  predCols<-seq(5,totalCol,5)
  
  
  for(e in seq(1:length(Envs)))
  {
    xName<-Envs[e]
    
    xImage<-readGDAL(paste(xName,".tif",sep = ""))
    
    xMatrix<-as.matrix(xImage)
    
    
    #x<-as.vector(xMatrix)
    #lmModel<-lm(y ~ x)
    #prediction<-predict(lmModel)
    #y<-y-prediction
    #yMatrixM<-matrix(y,nrow = totalRow, ncol = totalCol)
    
    disRange<-c(0.1,0.3,0.6,0.9)
    
    y<-as.vector(yMatrix)
    
    for(d in disRange)
    {
     
      disturb<-runif(length(y))
      y<-y+disturb*disRange[d]*y
      yMatrixM<-matrix(y,nrow = totalRow, ncol = totalCol)
      
      
      pred<-merge(predRows,predCols)
      
      startTime<-Sys.time()
      
      x_xmap_y <- GCCM(xMatrix, yMatrix, lib_sizes, lib, pred, E,cores=4)
      y_xmap_x <- GCCM(yMatrix,xMatrix, lib_sizes, lib, pred, E,cores=4)
      
      endTime<-Sys.time()
      
      print(difftime(endTime,startTime, units ="mins"))
      
      x_xmap_y$L <- as.factor(x_xmap_y$L)
      x_xmap_y_means <- do.call(rbind, lapply(split(x_xmap_y, x_xmap_y$L), function(x){max(0, mean(x$rho,na.rm=TRUE))}))
      
      
      y_xmap_x$L <- as.factor(y_xmap_x$L)
      y_xmap_x_means <- do.call(rbind, lapply(split(y_xmap_x, y_xmap_x$L), function(x){max(0, mean(x$rho,na.rm=TRUE))}))
      
      
      x_xmap_y_Sig<- significance(x_xmap_y_means,nrow(pred))
      y_xmap_x_Sig<- significance(y_xmap_x_means,nrow(pred))

      x_xmap_y_interval<- confidence(x_xmap_y_means,nrow(pred))
     colnames(x_xmap_y_interval)<-c("x_xmap_y_upper","x_xmap_y_lower")
  
     y_xmap_x_interval<- confidence(y_xmap_x_means,nrow(pred))
     colnames(y_xmap_x_interval)<-c("y_xmap_x_upper","y_xmap_x_lower")
      
      results<-data.frame(lib_sizes,x_xmap_y_means,y_xmap_x_means,x_xmap_y_Sig,y_xmap_x_Sig,x_xmap_y_interval,y_xmap_x_interval)
      
      write.csv(results,file=paste("results/HMSim/",disRange[d],xName,"_",yName,".csv",sep=""))
      
      par(mfrow=c(1,1))
      par(mar=c(5, 4, 4, 2) + 0.1)
      
      
      jpeg(filename = paste("results/HMSim/",disRange[d],xName,"_",yName,".jpg",sep = ""),width = 600, height = 400)
      
      plot(lib_sizes, x_xmap_y_means, type = "l", col = "royalblue", lwd = 2, 
           xlim = c(min(lib_sizes), max(lib_sizes)), ylim = c(0.0, 1), xlab = "L", ylab = expression(rho))
      lines(lib_sizes, y_xmap_x_means, col = "red3", lwd = 2)
      legend(min(lib_sizes), 1, legend = c("x xmap y", "y xmap x"), 
             xjust = 0, yjust = 1, lty = 1, lwd = 2, col = c("royalblue", "red3"))
      
      dev.off()
    }
    
  }                  
                     
}

sink()

