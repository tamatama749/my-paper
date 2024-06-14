setwd("E:\\Study\\R\\spatial-causality\\codes&data\\polygon")


library(parallel)
library(foreach)
library(doParallel)

#library("spdep")  #  read shape file data 

source("GCCM4Lattice.r")
source("basic.r")


load("popShp.RData")   #load data, If the data was not store previousely, the following codes could be used to read data from shape file


#columbus <- st_read(system.file("shapes/lifePoly.shp", package="spData")[1], quiet=TRUE)

#neighborMatrix <- poly2nb(as(columbus, "Spatial"))

#plot(st_geometry(columbus), border="grey")
#title(main=paste("Differences (red) in Columbus GAL weights (black)",
#                 "and polygon generated queen weights", sep="\n"), cex.main=0.6)
#class(columbus)



lib_sizes<-seq(10,2800,100)     # library sizes, will be the horizontal ordinate  of the reulst plot.
                                # The largest value ('to' parameter) can be set to the total number of spatial records,
                                # the 'by' can be set by takning accout to the computation time
E<-3                           # the dimensions of the embedings   

n <- NROW(columbus)            # get the total mumber of spatial records
lib <- c(1, n)                  # set the libray to confine the  spatial records jonint the construction of state spae 
pred <- c(1, n)                 # set the spatial records which will be predicted based on the   state spae




xNames<-c("DEM", 	"Tem",	"Pre",	"slop")    # Set the casue variables  

yName<-"popDensity"                         # Set the effect variable  

columbus<-as.data.frame(columbus)

y<-columbus[,yName] 

lmModel<-lm(as.formula(paste(yName,"~x_1+y_1",sep = "")),columbus )     #Remove the lieanr trend of effect variable  
prediction<-predict(lmModel)
y<-y-prediction

coords<-columbus[,c("x_1","y_1")]

for(xName in xNames)
  
{
  x<-columbus[,xName] 
  
  lmModel2<-lm(as.formula(paste(xName,"~x_1+y_1",sep = "")),columbus )     #Remove the lieanr trend of cause variable  
  prediction<-predict(lmModel2,coords)
  x<-x-prediction
  
  #lmModel<-lm(y ~ x)
  
  #prediction<-predict(lmModel)
  
  #y<-y-prediction
  
  startTime<-Sys.time()
  
  
  embedings<-generateEmbedings(neighborMatrix,x,E)                       #generate the  embedings of cause variable  
  x_xmap_y <- GCCMLattice(embedings, y, lib_sizes, lib, pred, E,cores=8) #predict y based on x  
  
   
  embedings<-generateEmbedings(neighborMatrix,y,E)                        #generate the  embedings of effect variable  
  y_xmap_x <- GCCMLattice(embedings, x, lib_sizes, lib, pred, E,cores=8)  #predict x based on y  
  
  
  endTime<-Sys.time()
  
  print(difftime(endTime,startTime, units ="mins"))
  
  x_xmap_y$L <- as.factor(x_xmap_y$L)
  x_xmap_y_means <- do.call(rbind, lapply(split(x_xmap_y, x_xmap_y$L), function(x){max(0, mean(x$rho,na.rm=TRUE))}))
                                                                       #calculate the mean of prediction accuray, measure by Pearson correlation
  
  
  y_xmap_x$L <- as.factor(y_xmap_x$L)
  y_xmap_x_means <- do.call(rbind, lapply(split(y_xmap_x, y_xmap_x$L), function(x){max(0, mean(x$rho,na.rm=TRUE))}))
                                                                    #calculate the mean of prediction accuray, measure by Pearson correlation
  
  
  x_xmap_y_Sig<- significance(x_xmap_y_means,pred[2])    #Test the significance of the prediciton accuray
  y_xmap_x_Sig<- significance(y_xmap_x_means,pred[2])    #Test the significance of the prediciton accuray
  
  x_xmap_y_interval<- confidence(x_xmap_y_means,pred[2]) #calculate the  95%. confidence interval  of the prediciton accuray
                                            
  colnames(x_xmap_y_interval)<-c("x_xmap_y_upper","x_xmap_y_lower")
  
  y_xmap_x_interval<- confidence(y_xmap_x_means,pred[2])
  colnames(y_xmap_x_interval)<-c("y_xmap_x_upper","y_xmap_x_lower")  #calculate the  95%. confidence interval of the prediciton accuray
  
  
  results<-data.frame(lib_sizes,x_xmap_y_means,y_xmap_x_means,x_xmap_y_Sig,y_xmap_x_Sig,x_xmap_y_interval,y_xmap_x_interval) #Save the detail results
  
  
  results<-data.frame(lib_sizes,x_xmap_y_means,y_xmap_x_means)
  
  write.csv(results,file=paste("results/Pop/",xName,"_",yName,"LatLon.csv",sep=""))   #Save the final results of cross-mapping predcition
  
  par(mfrow=c(1,1))
  par(mar=c(5, 4, 4, 2) + 0.1)
  
  
  
  jpeg(filename = paste("results/Pop/",xName,"_",yName,"LatLon.jpg",sep = ""),width = 600, height = 400)   #plot the final results of cross-mapping predcition
  
  plot(lib_sizes, x_xmap_y_means, type = "l", col = "royalblue", lwd = 2, 
       xlim = c(min(lib_sizes), max(lib_sizes)), ylim = c(0.0, 1), xlab = "L", ylab = expression(rho))
  lines(lib_sizes, y_xmap_x_means, col = "red3", lwd = 2)
  legend(min(lib_sizes), 1, legend = c("x xmap y", "y xmap x"), 
         xjust = 0, yjust = 1, lty = 1, lwd = 2, col = c("royalblue", "red3"))
  
  dev.off()
}








