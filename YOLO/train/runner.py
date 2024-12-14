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
        self.labels_dir = self.data_dir / 'labels'
        self.train_dir = self.output_dir / 'train'
        self.val_dir = self.output_dir / 'val'
        self.labeled_images_num = len(list(self.labels_dir.glob('*.json')))
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
    
    def copy_files(self, files, target_dir, is_labels=False):
        for file in files:
            if is_labels:
                # 处理标签文件
                src = self.labels_dir / file.name
                dst = target_dir / 'labels' / file.name
                if src.exists():
                    import shutil
                    shutil.copy2(src, dst)
            else:
                # 处理图片文件
                label_file = self.labels_dir / file.stem / '.txt' # 对应的标签文件有才可以继续复制 
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
        
        # 复制训练集
        self.copy_files(train_files, self.train_dir, is_labels=False)
        self.copy_files(train_files, self.train_dir, is_labels=True)
        
        # 复制验证集
        self.copy_files(val_files, self.val_dir, is_labels=False)
        self.copy_files(val_files, self.val_dir, is_labels=True)
        
        # 创建配置文件
        yaml_path = self.create_data_yaml(num_classes)
        
        return yaml_path



if __name__ == "__main__":
    main()