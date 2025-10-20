from ultralytics import YOLO
import os
import yaml
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

class YOLO_Runner:
    def __init__(self, data_dir = "data/YOLO/rawdata",output_dir = "data/YOLO/output"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.images_dir = self.data_dir / 'images'
        self.labels_dir = self.data_dir / 'labels_txt'
        self.train_dir = self.output_dir / 'train'
        self.val_dir = self.output_dir / 'val'
        self.labeled_images_num = len(list(self.labels_dir.glob('*.json')))
        self.model = YOLO(f'YOLO/model/yolo11n-seg.pt')
    def prepare_directories(self):
        dirs = [
            self.train_dir / 'images',
            self.train_dir / 'labels',
            self.val_dir / 'images',
            self.val_dir / 'labels'
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def split_dataset(self, val_size=0.2):
        image_files = list(self.images_dir.glob('*.jpg')) + list(self.images_dir.glob('*.png'))
        train_files, val_files = train_test_split(image_files, test_size=val_size, random_state=42)
        return train_files, val_files

    def set_model(self,model_name:str):
        self.model = YOLO(model_name)

    def copy_files(self, files, target_dir, is_labels=False):
        for file in files:
            if is_labels:
                # 处理标签文件
                src_name = file.stem + '.txt'  # 修改这里，直接使用.txt后缀
                src = self.labels_dir / src_name
                dst = target_dir / 'labels' / src_name
                print(f"Label source: {src}")
                print(f"Label exists: {src.exists()}")
                if src.exists():
                    import shutil
                    shutil.copy2(src, dst)
                    print(f"Copied label to: {dst}")
            else:
                # 处理图片文件
                label_file = self.labels_dir / (file.stem + '.txt')  # 方法1 # 对应的标签文件有才可以继续复制 
                if label_file.exists():  # 只有当对应的标签文件存在时才复制图片
                    src = file
                    dst = target_dir / 'images' / file.name
                    import shutil
                    shutil.copy2(src, dst)

    def create_data_yaml(self, num_classes):
        """创建数据配置文件"""
        data_yaml = {
            'train': 'train',
            'val': 'val',
            'nc': num_classes,
            'task': 'segment',
            'names': [f'class_{i}' for i in range(num_classes)]  # 替换为实际的类别名称
        }
        
        yaml_path = self.output_dir / 'data.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(data_yaml, f)
        
        return yaml_path
    
    def prepare_dataset(self, num_classes, val_size=0.2):
        self.prepare_directories()
        train_files, val_files = self.split_dataset(val_size)
        print(f'len of train_files: {len(train_files)}')
        # 复制训练集
        self.copy_files(train_files, self.train_dir, is_labels=True)
        self.copy_files(train_files, self.train_dir, is_labels=False)
        # 复制验证集
        self.copy_files(val_files, self.val_dir, is_labels=True)
        self.copy_files(val_files, self.val_dir, is_labels=False)
        
        
        # # 创建配置文件
        # yaml_path = self.create_data_yaml(num_classes)
        
        # return yaml_path
    def train_yolo_seg(self,data_yaml_path, model_size='n', epochs=100, batch_size=16):
        # 开始训练
        params = {
            'data': 'data/YOLO/output/data.yaml',
            'epochs': epochs,
            'batch': batch_size,
            'imgsz': 640,
            'patience': 50,
            'device': 0,  # GPU设备号，使用CPU则设为'cpu'
            'workers': 8,
            'seed': 42
        }
        results = self.model.train(**params)
        return  results

    def predict_segment(self, source, conf_threshold=0.25, video_output=None):
        """
        处理图像或视频的预测函数
        source: 可以是图片路径或视频路径
        conf_threshold: 置信度阈值
        video_output: 输出视频的保存路径（如果是视频）
        """
        # 检查输入是图片还是视频
        source_path = Path(source)
        if source_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
            # 视频处理
            cap = cv2.VideoCapture(str(source_path))
            if not cap.isOpened():
                print("Error: Cannot open video file")
                return None

            # 获取视频属性
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))

            # 设置视频写入器（如果需要保存）
            if video_output:
                out = cv2.VideoWriter(
                    video_output,
                    cv2.VideoWriter_fourcc(*'mp4v'),
                    fps,
                    (frame_width, frame_height)
                )

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 对当前帧进行预测
                results = self.model.predict(
                    source=frame,
                    conf=conf_threshold,
                    show=True,  # 实时显示
                    stream=True  # 流式处理
                )

                # 处理预测结果
                for r in results:
                    # 获取处理后的帧
                    plotted_frame = r.plot()
                    
                    # 显示处理后的帧
                    cv2.imshow('YOLOv8 Prediction', plotted_frame)

                    # 保存处理后的帧（如果需要）
                    if video_output:
                        out.write(plotted_frame)

                # 按'q'退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # 清理资源
            cap.release()
            if video_output:
                out.release()
            cv2.destroyAllWindows()

        else:
            # 图片处理（原有的处理方式）
            results = self.model.predict(
                source=source,
                conf=conf_threshold,
                save=True
            )
            return results

    def evaluate_model(self, val_dir):
        metrics = self.model.val()
        return metrics
