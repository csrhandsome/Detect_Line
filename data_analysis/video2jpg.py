from util.cv_util import *
def video2jpg():
    frames=video2frames('data/YOLO/video/running.mp4',200)
    print(f'有{len(frames)}帧')
    # present_frame(frames)
    frames2jpg(frames)