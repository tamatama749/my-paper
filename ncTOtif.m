
clc
clear all


ncFilePath=['H:\basicData\中国气象数据\nc\PRCP_month_20\pre_2020.nc'];
     lon=ncread(ncFilePath,'lon');
     lat=ncread(ncFilePath,'lat');
     time=ncread(ncFilePath,'time');
     tmp=ncread(ncFilePath,'pre'); 
     k=0;
    for y=2020    %如果读取的是tmp_2015_2017.nc此处对应改成2015:2017
         for j=1:12
             k=k+1;
         tmp1=tmp(:,:,k); 
         data=flipud(tmp1');
         data(data==-32768)=NaN;
         R = georasterref('RasterSize', size(data),'Latlim', [double(min(lat)) double(max(lat))], 'Lonlim', [double(min(lon)) double(max(lon))]);%地理栅格数据参考对象(类)
         filename1=['H:\basicData\中国气象数据\nc\tif\',num2str(y),'_',num2str(j),'.tif'];
         geotiffwrite(filename1,data,R);
         end
         disp([num2str(y),'done'])
    end
     disp('finish!')