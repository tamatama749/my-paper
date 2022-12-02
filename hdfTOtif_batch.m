clc;
clear;
close all
%% ����ȡHDF5�ļ���׼������
datadir = 'H:\basicData\ȫ������ŷ����ݼ�GFED4\'; %ָ�������������ڵ��ļ���
filelist = dir([datadir,'*.hdf5']);       %�г���������ָ�����͵��ļ�
% a = filelist(1).name;                 %�鿴Ҫ��ȡ���ļ��ı��
% b = filelist(2).name;
k=length(filelist);

%%��һ�� չʾh5�ļ��Ľṹ������ ����group ����dataset �Լ��������ԣ�
%h5info('H:\basicData\ȫ������ŷ����ݼ�GFED4\GFED4.1s_2001.hdf5')

%%�ڶ��� չʾ����group����Ϣ���鵽������Ҫ�����ݼ��������Լ�����group
%h5disp('H:\basicData\ȫ������ŷ����ݼ�GFED4\GFED4.1s_2001.hdf5','/')

for i = 1:k  %���ζ�ȡ������
    
    %% ������ȡ�ļ�
    ncFilePath = ['H:\basicData\ȫ������ŷ����ݼ�GFED4\',filelist(i).name]; %�趨NC·��
    num = filelist(i).name(1:13); %��ȡ���ݱ�ţ��Ա��ڱ���ʱ�Դ˱�Ŵ���tif
      
   
    
    %% ��ȡ����ֵ
    %������ �鵽������Ҫ����Ϣ����ȡ������ʽΪ data = h5read(filename,datasetname) �㼶��ϵ�á�/����ʾ
SM_am = h5read(ncFilePath...
    ,'/emissions/12/DM');

%���Ĳ� ����������뾭γ�ȿ��ܲ���Ӧ����˶Ծ�����з�ת��ת�õȣ���һ�����Լ���Ҫ
SM_am = permute(SM_am,[2,1]);
SM_am = flipud(SM_am);
%���岽 ����դ�����ݵĵ���ռ�ο������С�85.0445�͡�180�Ǿ�γ�ȷ�Χ
R = georasterref('RasterSize', size(SM_am),'Latlim', [double(-90)...
    double(90)], 'Lonlim', [double(-180) double(180)]);
    


    %% ��Ϊtif��ʽ
    %������ ���tif
   
    geotiffwrite(['H:\basicData\ȫ������ŷ����ݼ�GFED4\test\',num,'_12DM.tif'],SM_am,R);
    disp([num,'done'])
    
end
disp('finish!')
