#encoding=gbk
import os
def main (path):
    filename_list = os.listdir(path)
    """os.listdir(path) ɨ��·�����ļ������ļ�����������б�"""

    a = 0
    for i in filename_list:
        used_name = path + filename_list[a]
        new_name = path + filename_list[a].replace(LANDSAT_PRODUCT_ID,LANDSAT_SCENE_ID)
        new_name = new_name.replace("bt","toa")
        os.rename(used_name, new_name)
        print("�ļ�%s�������ɹ����µ��ļ���Ϊ%s" %(used_name,new_name))
        a += 1

if __name__=='__main__':
    path="H:/basicData/VCTpreparation/fanghuoyinxiang/LC081190242014080701T1-SC20220611051354/" # Ŀ��·��
    LANDSAT_PRODUCT_ID = "LC08_L1TP_119024_20140807_20170420_01_T1"
    LANDSAT_SCENE_ID = "LC81190242014219LGN01"
    main(path)