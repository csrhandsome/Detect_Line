import cv2
import os
from ultralytics import YOLO
from pathlib import Path
def video2frames(video_path, frame_num):
    video_path = str(Path(video_path))# 确保路径无误
    # 打开视频文件
    #根据select_cap函数选出的backend
    cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("Failed to open video with CAP_FFMPEG")
    # 获取视频的总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps=cap.get(cv2.CAP_PROP_FPS)
    # 如果要每一帧都截取则加上这个 frame_num = total_frames
    step = 20 # 采样间隔
    frames = []
    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        if frame_count % step == 0 and len(frames) < frame_num:
            # OpenCV读取的是BGR格式，转换为RGB
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 转换为tensor并添加到列表
            frames.append(frame)
        frame_count += 1
        if len(frames) == frame_num:
            break
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    cap.release()
    return frames

def present_frame(frames):
    for frame in frames:
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
                break

def frames2jpg(frames, output_dir='data/YOLO/rawdata/images'):
    for i, frame in enumerate(frames):
        cv2.imwrite(os.path.join(output_dir, f"frame_{i}.jpg"), frame)
def normal_YOLO_through_camera():
    # Load the YOLO11 model
    model = YOLO("YOLO/model/yolo11n-seg.pt")
    
    # Open the video file
    # video_path = "path/to/video.mp4"
    video_path = 0
    cap = cv2.VideoCapture('data/YOLO/video/running.mp4')
    
    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
    
        if success:
            # Run YOLO11 tracking on the frame, persisting tracks between frames
            results = model.track(frame, persist=True)
    
            # Visualize the results on the frame
            annotated_frame = results[0].plot()
    
            # Display the annotated frame
            cv2.imshow("YOLO11 Tracking", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break
    
    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

def labelme2mask(self, label_names):
        """
        将labelme的json文件转换为mask
        label_names: 标签名称列表，例如 ['background', 'class1', 'class2']
        """
        self.temp_masks_dir.mkdir(parents=True, exist_ok=True)
        self.temp_images_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建标签到索引的映射
        label_to_idx = {label: idx for idx, label in enumerate(label_names)}
        
        for json_path in self.json_dir.glob('*.json'):
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # 获取图像尺寸
            img_height = json_data['imageHeight']
            img_width = json_data['imageWidth']
            
            # 创建空白mask
            mask = np.zeros((img_height, img_width), dtype=np.uint8)
            
            # 处理每个标注对象
            for shape in json_data['shapes']:
                label = shape['label']
                if label not in label_to_idx:
                    continue
                    
                points = np.array(shape['points'], dtype=np.int32)
                label_idx = label_to_idx[label]
                
                # 填充多边形区域
                cv2.fillPoly(mask, [points], label_idx)
            
            # 保存mask
            mask_path = self.temp_masks_dir / f"{json_path.stem}.png"
            Image.fromarray(mask).save(mask_path)
            
            # 复制原始图像
            img_path = json_path.parent / json_data['imagePath']
            if img_path.exists():
                shutil.copy2(img_path, self.temp_images_dir / img_path.name)