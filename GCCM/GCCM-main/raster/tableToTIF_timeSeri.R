install.packages("readr")
install.packages("raster")
library(readr)
library(raster)

file_path <- "C:/Users/suhui/Documents/马伟波-论文复现/data/逐年统计数据.csv"
data <- read_csv(file_path)

# 获取所有列名
column_names <- colnames(data)

variable_names <- setdiff(column_names, c("城市", "编号"))
# 排除变量名中的年份和单位信息
variable_names_no_year <- gsub("20[0-9]{2}年", "", variable_names)
variable_names_no_year <- gsub("\\（.*?\\）", "", variable_names_no_year)
variable_names_no_year <- unique(variable_names_no_year)
# 打印去除了年份和括号单位的变量名称
print(variable_names_no_year)

# 过滤出含有“碳排放量”的列名
# carbon_emission_columns <- grep("单位GDP碳排放量", column_names, value = TRUE)

# 创建一个8x8的空矩阵模板
matrix_template <- matrix(NA, nrow = 8, ncol = 8)

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
# 定义输出目录
output_dir <- "C:/Users/suhui/Documents/马伟波-论文复现/data/timeSeriTIF/"

# 检查并创建输出目录
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# 打印输出目录以调试
print(paste("Output directory:", output_dir))

# 遍历每个变量名称并生成对应的TIF文件
for (variable_name in variable_names_no_year) {
  # 过滤出当前变量相关的列名
  variable_columns <- grep(variable_name, column_names, value = TRUE)
  
  # 初始化栅格砖块对象列表
  raster_list <- list()
  
  # 遍历所有相关的列名
  for (column_name in variable_columns) {
    # 获取城市名和对应的值
    city_values <- data[, c("城市", column_name)]
    
    # 创建一个新的矩阵
    city_matrix <- matrix_template
    
    # 遍历城市并将对应的值赋给矩阵中的相应位置
    for (i in 1:nrow(city_values)) {
      city <- city_values$城市[i]
      if (!is.na(city)) {
        value <- city_values[[column_name]][i]
        if (city %in% names(city_positions)) {
          pos <- city_positions[[city]]
          city_matrix[pos[1], pos[2]] <- value
        }
      }
    }
    
    # 将矩阵转换为栅格对象
    r <- raster(city_matrix)
    names(r) <- column_name
    raster_list[[column_name]] <- r
  }
  
  # 确保raster_list不为空
  if (length(raster_list) > 0) {
    # 将所有栅格对象组合成一个砖块对象
    raster_brick <- brick(raster_list)
    
    # 打印文件路径以调试
    output_path <- paste0(output_dir, variable_name, ".tif")
    print(paste("Saving file to:", output_path))
    
    # 保存为多图层的TIFF文件
    writeRaster(raster_brick, output_path, format="GTiff", overwrite=TRUE)
    
    print(paste(variable_name, "TIFF文件已成功生成并保存"))
  } else {
    print(paste(variable_name, "没有有效数据生成TIFF文件"))
  }
}
