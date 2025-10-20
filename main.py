from YOLO.train.train import train
from YOLO.eval.eval import eval
from util.cv_util import normal_YOLO_through_camera, receive_video_with_socket
from M5stack.imureceiver_udp import receive_imu
import threading

if __name__ == "__main__":
    # -------------training--------------
    # train()
    # -------------evaluation-------------
    # model_name = 'runs/segment/train/weights/best.pt'
    # normal_YOLO_through_camera(model_name=model_name)
    # -------------real_world-------------
    receive_video_with_socket(use_raspberrypi=False)
    # receive_imu()
