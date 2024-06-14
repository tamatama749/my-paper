GCCMSingle4Lattice<-function(x_vectors,y,lib_indices,lib_size,max_lib_size,possible_lib_indices,pred_indices,b)
{
  n <- NROW(x_vectors) 
   x_xmap_y <- data.frame()
  
   if(lib_size == max_lib_size) # no possible lib variation if using all vectors
  {
    lib_indices <- rep.int(FALSE, times = n)
    lib_indices[possible_lib_indices] <- TRUE
    
    # run cross map and store results
    results <- simplex_projection(x_vectors, y, lib_indices, pred_indices, b)
    x_xmap_y <- rbind(x_xmap_y, data.frame(L = lib_size, rho = results$stats$rho))
  }
  else
  {
    for(start_lib in 1:max_lib_size)
    {
      lib_indices <- rep.int(FALSE, times = n)
      # setup changing library
      if(start_lib+lib_size-1 > max_lib_size) # loop around to beginning of lib indices
      {
        lib_indices[possible_lib_indices[start_lib:max_lib_size]] <- TRUE
        num_vectors_remaining <- lib_size - (max_lib_size-start_lib+1)
        lib_indices[possible_lib_indices[1:num_vectors_remaining]] <- TRUE
      }
      else
      {
        lib_indices[possible_lib_indices[start_lib:(start_lib+lib_size-1)]] <- TRUE
      }
      
      # run cross map and store results
      results <- simplex_projection(x_vectors, y, lib_indices, pred_indices, b)
      x_xmap_y <- rbind(x_xmap_y, data.frame(L = lib_size, rho = results$stats$rho)) 
    }
  }
   return(x_xmap_y)
}




laggedVar4Lattic<- function (spNeighbor,lagNum)
{
  
  lagSpNeighbor<- spNeighbor
  
  if (lagNum<1)
  {
    
    return (NULL)
  }else if(lagNum>1)
  {
    #preSpNeighbor<-spNeighbor
    
    curSpNeighbor<-spNeighbor
    
    for(lag in 1:(lagNum-1) )
    {
      
      preSpNeighbor<-curSpNeighbor
      
      for(i in 1: length(preSpNeighbor))
      {
        curChain <-preSpNeighbor[[i]]
        
        newRings<-curChain
        
        for(neigh in 1: length (curChain))
        {
          nextChainID<-curChain[neigh]
          
          
          if(nextChainID>0)
          {
            nextChain<- spNeighbor[[nextChainID]]
            
            newRings<-unique(c(newRings, nextChain))
          }
          
          
        }
        
        curSpNeighbor[[i]]<-newRings
      }
      
    }
    
    for(i in 1: length(preSpNeighbor))
    {
      
      lagSpNeighbor[[i]]<- curSpNeighbor[[i]][!(curSpNeighbor[[i]] %in% c(preSpNeighbor[[i]],i))]
      
    }
    
  }
  
  return(lagSpNeighbor)
  
}

generateEmbedings<- function (neighborMatrix,x,E)
{
  n <- NROW(x)
  xEmbedings <- matrix(NaN, nrow = n, ncol = E)

  
  for(lagNum in 1:E)
  {
    laggedResults<-laggedVar4Lattic(neighborMatrix,lagNum)
    
    for(l in 1:length (laggedResults))
    {
      neighbors<-laggedResults[[l]]
      
      neighborValues<-x[neighbors]
      
      xEmbedings[l,lagNum]<-mean(neighborValues)
      
    }
    
  }
  
  return (xEmbedings)
}


GCCMLattice <- function(x_vectors, y, lib_sizes, lib, pred, E, tau = 1, b = E+1,cores=NULL)
{
  # do convergent cross mapping using simplex projection
  # x           = time series to cross map from
  # y           = time series to cross map to
  # lib_sizes   = vector of library sizes to use
  # lib         = matrix (n x 2) using n sequences of data to construct libraries
  # pred        = matrix (n x 2) using n sequences of data to predict from
  # E           = number of dimensions for the attractor reconstruction
  # tau         = time lag for the lagged-vector construction
  # b           = number of nearest neighbors to use for prediction
  
  n <- NROW(x_vectors)
  pred <- matrix(pred, ncol = 2, byrow = TRUE)
  lib <- matrix(lib, ncol = 2, byrow = TRUE)
  
  
  
  # setup pred_indices
  pred_indices <- rep.int(FALSE, times = n)
  for(i in 1:NROW(pred))
  {
    row_start <- pred[i, 1] + (E-1)*tau
    row_end <- pred[i, 2]
    if(row_end > row_start)
      pred_indices[row_start:row_end] <- TRUE
  }
  
  # setup lib_indices
  lib_indices <- rep.int(FALSE, times = n)
  for(i in 1:NROW(lib))
  {
    row_start <- lib[i, 1] + (E-1)*tau
    row_end <- lib[i, 2]
    if(row_end > row_start)
      lib_indices[row_start:row_end] <- TRUE
  }
  max_lib_size <- sum(lib_indices) # maximum lib size
  possible_lib_indices <- which(lib_indices) # create vector of usable lib vectors
  
  # make sure max lib size not exceeded and remove duplicates
  lib_sizes <- unique(pmin(max_lib_size, lib_sizes))
  
  x_xmap_y <- data.frame()
  
  
  if(is.null(cores))
  {
    for(lib_size in lib_sizes)
    {
      
      x_xmap_y<-rbind(x_xmap_y,GCCMSingle4Lattice(x_vectors,y,lib_indices,lib_size,max_lib_size,possible_lib_indices,pred_indices,b))
      
    }
  }else
  {
    cl <- makeCluster(cores)
    registerDoParallel(cl)
    clusterExport(cl,deparse(substitute(GCCMSingle4Lattice)))
    #clusterExport(cl,deparse(substitute(locate)))
    clusterExport(cl,deparse(substitute(simplex_projection)))
    #clusterExport(cl,deparse(substitute(distance_Com)))
    clusterExport(cl,deparse(substitute(compute_stats)))
    
    x_xmap_y <- foreach(lib_size=lib_sizes, .combine='rbind') %dopar% GCCMSingle4Lattice(x_vectors,y,lib_indices,lib_size,max_lib_size,possible_lib_indices,pred_indices,b)
    
   
    
    stopCluster(cl)
  }
  
 
  return(x_xmap_y)
}

univariate_SSR <- function(data, lib, pred, E, tau = 1, tp = 1, b = E+1)
{
  # do univariate prediction using simplex projection
  # data = time series
  # lib = matrix (n x 2) using n sequences of data for library
  # pred = matrix (n x 2) using n sequences of data to predict from
  # E = number of dimensions for the attractor reconstruction
  # tau = time lag for the lagged-vector construction
  # tp = time step for future predictions
  # b = number of nearest neighbors to use for prediction
  
  n <- NROW(data)
  lib <- matrix(lib, ncol = 2)
  pred <- matrix(pred, ncol = 2)
  
  # setup vectors
  vectors <- matrix(NaN, nrow = n, ncol = E)
  lag <- 0
  for (i in 1:E)
  {
    vectors[(lag+1):n,i] <- data[1:(n-lag)]
    lag <- lag + tau
  }
  
  # setup lib_indices
  lib_indices <- rep.int(FALSE, times = n)
  for(i in 1:NROW(lib))
  {
    row_start <- lib[i, 1] + (E-1)*tau
    row_end <- lib[i, 2] - tp
    if(row_end > row_start)
      lib_indices[row_start:row_end] <- TRUE
  }
  
  # setup pred_indices
  pred_indices <- rep.int(FALSE, times = n)
  for(i in 1:NROW(pred))
  {
    row_start <- pred[i, 1] + (E-1)*tau
    row_end <- pred[i, 2] - tp
    if(row_end > row_start)
      pred_indices[row_start:row_end] <- TRUE
  }
  
  # setup target
  target <- rep.int(NaN, times = n)
  target[1:(n-tp)] <- data[(1+tp):n]
  
  return(simplex_projection(vectors, target, lib_indices, pred_indices, b))
}

simplex_projection <- function(vectors, target, lib_indices, pred_indices, num_neighbors)
{
  # do simplex projection
  # vectors = reconstructed state-space (each row is a separate vector/state)
  # target = time series to be used as the target (should line up with vectors)
  # lib_indices = vector of T/F values (which states to include when searching for neighbors)
  # pred_indices = vector of T/F values (which states to predict from)
  # num_neighbors = number of neighbors to use for simplex projection
  
  # setup output
  pred <- rep.int(NaN, times = length(target))
  
  # make predictions
  for(p in which(pred_indices))
  {
    temp_lib <- lib_indices[p]
    lib_indices[p] <- FALSE
    libs <- which(lib_indices)
    
    # compute distances
    q <- matrix(rep(vectors[p,], length(libs)), nrow = length(libs), byrow = T)
    
    dis<-(vectors[libs,] - q)^2 
    distances <- sqrt(rowSums(dis,na.rm = TRUE)/rowSums(!is.na(dis)))  ###Bingbo added, to handle NA 
    
    # find nearest neighbors
    neighbors <- order(distances)[1:num_neighbors]
    min_distance <- distances[neighbors[1]]
    
    # compute weights
    if(min_distance == 0) # perfect match
    {
      weights <- rep.int(0.000001, times = num_neighbors)
      weights[distances[neighbors] == 0] <- 1
    }
    else
    {
      weights <- exp(-distances[neighbors]/min_distance)
      weights[weights < 0.000001] <- 0.000001
    }
    total_weight <- sum(weights)
    
    # make prediction
    pred[p] <- (weights %*% target[libs[neighbors]]) / total_weight
    
    lib_indices[p] <- temp_lib 
  }
  
  # return output & stats
  return(list(pred = pred, stats = compute_stats(target[pred_indices], pred[pred_indices])))
}

compute_stats <- function(obs, pred)
{
  # computes performance metrics for how well predictions match observations
  # obs = vector of observations
  # pred = vector of prediction
  
  N = sum(is.finite(obs) & is.finite(pred))
  rho = cor(obs, pred, use = "pairwise.complete.obs")
  mae = mean(abs(obs-pred), na.rm = TRUE)
  rmse = sqrt(mean((obs-pred)^2, na.rm = TRUE))
  return(data.frame(N = N, rho = rho, mae = mae, rmse = rmse))
}



