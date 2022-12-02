clc
clear
close all

%%第一步 展示h5文件的结构（名字 几个group 几个dataset 以及其他属性）
%h5info('H:\basicData\全球火灾排放数据集GFED4\GFED4.1s_2003.hdf5')

%%第二步 展示所有group的信息，查到我们需要的数据集的名字以及所在group
%h5disp('H:\basicData\全球火灾排放数据集GFED4\GFED4.1s_2003.hdf5','/')

%第三步 查到我们需要的信息后，提取变量格式为 data = h5read(filename,datasetname) 层级关系用‘/’表示
SM_am = h5read('H:\basicData\全球火灾排放数据集GFED4\GFED4.1s_2003.hdf5'...
    ,'/emissions/03/partitioning/DM_BORF');

%第四步 矩阵的行列与经纬度可能不对应，因此对矩阵进行翻转、转置等，这一步看自己需要
SM_am = permute(SM_am,[2,1]);
SM_am = flipud(SM_am);

%第五步 生成栅格数据的地理空间参考，其中±85.0445和±180是经纬度范围
R = georasterref('RasterSize', size(SM_am),'Latlim', [double(-90)...
    double(90)], 'Lonlim', [double(-180) double(180)]);
    
%第六步 输出tif
geotiffwrite(['H:\basicData\全球火灾排放数据集GFED4\test\','2001.tif'],SM_am,R);
disp('finish!')
%如果数据格式是hdf，记得把命令h5read改成hdfread，其他的命令也是一样h5info→hdfinfo