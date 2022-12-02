clc
clear
close all

%%��һ�� չʾh5�ļ��Ľṹ������ ����group ����dataset �Լ��������ԣ�
%h5info('H:\basicData\ȫ������ŷ����ݼ�GFED4\GFED4.1s_2003.hdf5')

%%�ڶ��� չʾ����group����Ϣ���鵽������Ҫ�����ݼ��������Լ�����group
%h5disp('H:\basicData\ȫ������ŷ����ݼ�GFED4\GFED4.1s_2003.hdf5','/')

%������ �鵽������Ҫ����Ϣ����ȡ������ʽΪ data = h5read(filename,datasetname) �㼶��ϵ�á�/����ʾ
SM_am = h5read('H:\basicData\ȫ������ŷ����ݼ�GFED4\GFED4.1s_2003.hdf5'...
    ,'/emissions/03/partitioning/DM_BORF');

%���Ĳ� ����������뾭γ�ȿ��ܲ���Ӧ����˶Ծ�����з�ת��ת�õȣ���һ�����Լ���Ҫ
SM_am = permute(SM_am,[2,1]);
SM_am = flipud(SM_am);

%���岽 ����դ�����ݵĵ���ռ�ο������С�85.0445�͡�180�Ǿ�γ�ȷ�Χ
R = georasterref('RasterSize', size(SM_am),'Latlim', [double(-90)...
    double(90)], 'Lonlim', [double(-180) double(180)]);
    
%������ ���tif
geotiffwrite(['H:\basicData\ȫ������ŷ����ݼ�GFED4\test\','2001.tif'],SM_am,R);
disp('finish!')
%������ݸ�ʽ��hdf���ǵð�����h5read�ĳ�hdfread������������Ҳ��һ��h5info��hdfinfo