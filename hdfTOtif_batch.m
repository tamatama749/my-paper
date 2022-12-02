clc;
clear;
close all
%% 批读取HDF5文件的准备工作
datadir = 'H:\basicData\全球火灾排放数据集GFED4\'; %指定批量数据所在的文件夹
filelist = dir([datadir,'*.hdf5']);       %列出所有满足指定类型的文件
% a = filelist(1).name;                 %查看要读取的文件的编号
% b = filelist(2).name;
k=length(filelist);

%%第一步 展示h5文件的结构（名字 几个group 几个dataset 以及其他属性）
%h5info('H:\basicData\全球火灾排放数据集GFED4\GFED4.1s_2001.hdf5')

%%第二步 展示所有group的信息，查到我们需要的数据集的名字以及所在group
%h5disp('H:\basicData\全球火灾排放数据集GFED4\GFED4.1s_2001.hdf5','/')

for i = 1:k  %依次读取并处理
    
    %% 批量读取文件
    ncFilePath = ['H:\basicData\全球火灾排放数据集GFED4\',filelist(i).name]; %设定NC路径
    num = filelist(i).name(1:13); %读取数据编号，以便于保存时以此编号储存tif
      
   
    
    %% 读取变量值
    %第三步 查到我们需要的信息后，提取变量格式为 data = h5read(filename,datasetname) 层级关系用‘/’表示
SM_am = h5read(ncFilePath...
    ,'/emissions/12/DM');

%第四步 矩阵的行列与经纬度可能不对应，因此对矩阵进行翻转、转置等，这一步看自己需要
SM_am = permute(SM_am,[2,1]);
SM_am = flipud(SM_am);
%第五步 生成栅格数据的地理空间参考，其中±85.0445和±180是经纬度范围
R = georasterref('RasterSize', size(SM_am),'Latlim', [double(-90)...
    double(90)], 'Lonlim', [double(-180) double(180)]);
    


    %% 存为tif格式
    %第六步 输出tif
   
    geotiffwrite(['H:\basicData\全球火灾排放数据集GFED4\test\',num,'_12DM.tif'],SM_am,R);
    disp([num,'done'])
    
end
disp('finish!')
