from pathlib import Path
import numpy as np
from PIL import Image
import cv2
def check_labels(dataset_path):
    dataset_path = Path(dataset_path)
    
    for split in ['train', 'val']:
        labels_dir = dataset_path / split / 'masks'
        if not labels_dir.exists():
            print(f"错误: {labels_dir} 不存在")
            continue
            
        print(f"\n检查 {split} 集标签:")
        label_files = list(labels_dir.glob('*.txt'))
        
        if not label_files:
            print(f"错误: {labels_dir} 中没有txt文件")
            continue
            
        for label_file in label_files:
            mask = np.array(Image.open(label_file))
            unique_values = np.unique(mask)
            print(f"{label_file.name}: 包含的类别值 = {unique_values}")
            
            # 检查是否全为背景（全0）
            if len(unique_values) == 1 and unique_values[0] == 0:
                print(f"警告: {label_file.name} 全为背景!")

def check_image_label_pairs(dataset_path):
    dataset_path = Path(dataset_path)
    
    for split in ['train', 'val']:
        print(f"\n检查 {split} 集的图像-标签对：")
        images_dir = dataset_path / split / 'images'
        labels_dir = dataset_path / split / 'masks'
        
        # 检查图像文件
        image_files = sorted(images_dir.glob('*.jpg'))  # 也检查 .jpeg, .png
        if not image_files:
            image_files = sorted(images_dir.glob('*.jpeg'))
        if not image_files:
            image_files = sorted(images_dir.glob('*.txt'))
            
        print(f"图像文件:")
        for img_path in image_files:
            label_path = labels_dir / f"{img_path.stem}.txt"
            print(f"图像: {img_path.name} -> 标签: {label_path.name} "
                  f"(标签存在: {label_path.exists()})")
            
            if label_path.exists():
                # 检查图像和标签尺寸是否匹配
                img = cv2.imread(str(img_path))
                mask = cv2.imread(str(label_path), 0)  # 以灰度图方式读取
                if img.shape[:2] != mask.shape:
                    print(f"警告: 尺寸不匹配! 图像: {img.shape[:2]}, 标签: {mask.shape}")