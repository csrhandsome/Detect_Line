import json
import os
import numpy as np
from PIL import Image
import cv2
from pathlib import Path

def json2png(label_names=['line'], json_dir='data/YOLO/rawdata/json', output_dir='data/YOLO/rawdata/masks'):
    # 修改标签映射，索引从1开始 重要
    label_to_idx = {label: idx for idx, label in enumerate(label_names)}
    print(f"标签映射: {label_to_idx}")  # 调试用
    
    json_files = list(Path(json_dir).glob('*.json'))
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        img_height = json_data['imageHeight']
        img_width = json_data['imageWidth']
        
        # 创建掩码，默认为0（背景）
        mask = np.zeros((img_height, img_width), dtype=np.uint8)
        
        for shape in json_data['shapes']:
            label = shape['label']
            if label not in label_to_idx:
                print(f"警告: 未知标签 {label}")
                continue
            
            points = np.array(shape['points'], dtype=np.int32)
            label_idx = label_to_idx[label]
            
            if shape['shape_type'] == 'polygon':
                cv2.fillPoly(mask, [points], label_idx)
            elif shape['shape_type'] == 'rectangle':
                cv2.rectangle(mask, 
                            tuple(points[0].astype(int)), 
                            tuple(points[1].astype(int)), 
                            label_idx, 
                            -1)
        
        # 验证掩码是否为空
        if np.max(mask) == 0:
            print(f"警告: {json_file.name} 生成的掩码全为背景")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        mask_path = output_dir / f"{json_file.stem}.png"
        Image.fromarray(mask).save(mask_path)
        
        print(f"处理: {json_file.name} -> {mask_path}")
        print(f"掩码中的唯一值: {np.unique(mask)}")  # 调试用


def json2txt(json_dir='data/YOLO/rawdata/json', output_dir='data/YOLO/rawdata/labels', 
        label_names=['line'], image_height=None, image_width=None):
    # 创建标签到索引的映射
    label_to_idx = {label: idx for idx, label in enumerate(label_names)}
    
    # 确保输出目录存在
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有JSON文件
    json_files = list(Path(json_dir).glob('*.json'))
    print(f"找到 {len(json_files)} 个JSON文件")
    
    for json_file in json_files:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取图像尺寸
        img_height = image_height or data['imageHeight']
        img_width = image_width or data['imageWidth']
        
        # 创建对应的TXT文件
        txt_path = output_dir / f"{json_file.stem}.txt"
        if txt_path.exists():
            print(f"跳过已存在的TXT文件: {txt_path}")
        else:
            with open(txt_path, 'w', encoding='utf-8') as f:
                # 处理每个标注对象
                for shape in data['shapes']:
                    label = shape['label']
                    if label not in label_to_idx:
                        print(f"警告: 跳过未知标签 {label} in {json_file.name}")
                        continue
                    
                    # 获取标签索引
                    label_idx = label_to_idx[label]
                    
                    # 获取多边形点坐标
                    points = np.array(shape['points'])
                    
                    # 归一化坐标
                    points[:, 0] = points[:, 0] / img_width
                    points[:, 1] = points[:, 1] / img_height
                    
                    # 确保所有坐标在[0,1]范围内
                    points = np.clip(points, 0, 1)
                    
                    # 格式化为YOLO格式：class_id x1 y1 x2 y2 ...
                    points_str = ' '.join([f"{x:.6f} {y:.6f}" for x, y in points])
                    f.write(f"{label_idx} {points_str}\n")
        
    print(f"转换完成 TXT文件保存在: {output_dir}")