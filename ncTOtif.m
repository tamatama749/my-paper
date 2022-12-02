
clc
clear all


ncFilePath=['H:\basicData\�й���������\nc\PRCP_month_20\pre_2020.nc'];
     lon=ncread(ncFilePath,'lon');
     lat=ncread(ncFilePath,'lat');
     time=ncread(ncFilePath,'time');
     tmp=ncread(ncFilePath,'pre'); 
     k=0;
    for y=2020    %�����ȡ����tmp_2015_2017.nc�˴���Ӧ�ĳ�2015:2017
         for j=1:12
             k=k+1;
         tmp1=tmp(:,:,k); 
         data=flipud(tmp1');
         data(data==-32768)=NaN;
         R = georasterref('RasterSize', size(data),'Latlim', [double(min(lat)) double(max(lat))], 'Lonlim', [double(min(lon)) double(max(lon))]);%����դ�����ݲο�����(��)
         filename1=['H:\basicData\�й���������\nc\tif\',num2str(y),'_',num2str(j),'.tif'];
         geotiffwrite(filename1,data,R);
         end
         disp([num2str(y),'done'])
    end
     disp('finish!')