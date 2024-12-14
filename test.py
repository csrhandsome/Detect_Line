from data_analysis.video2jpg import video2jpg
from data_analysis.json2mask import json2png,json2txt
from util.check_util import check_labels, check_image_label_pairs
from util.cv_util import normal_YOLO_through_camera
if __name__ == '__main__':
    json2txt()
    # normal_YOLO_through_camera()
    #check_labels('data/YOLO/output')
    #check_image_label_pairs('data/YOLO/output')