from YOLO.train.runner import YOLO_Runner
from ultralytics import YOLO
def train_yolo_seg(data_yaml_path, model_size='n', epochs=100, batch_size=16):
    # 加载预训练模型
    model = YOLO(f'YOLO/model/yolo11n.pt')
    # 训练参数
    params = {
        'data': data_yaml_path,
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': 640,
        'patience': 50,
        'device': 0,  # GPU设备号，使用CPU则设为'cpu'
        'workers': 8,
        'seed': 42
    }
    # 开始训练
    results = model.train(**params)
    return model, results

def predict_segment(model, image_path, conf_threshold=0.25):
    results = model.predict(
        source=image_path,
        conf=conf_threshold,
        save=True
    )
    return results

def evaluate_model(model, val_dir):
    metrics = model.val()
    return metrics

def train():
    # 分割类别数量
    num_classes = 1   
    # 初始化训练器
    trainer = YOLO_Runner(data_dir="data/YOLO/rawdata",output_dir="data/YOLO/output")

    # 准备数据集
    yaml_path = trainer.prepare_dataset(num_classes, val_size=0.2)
    # 训练模型
    model, results = train_yolo_seg(
        data_yaml_path=yaml_path,
        model_size='n',  # n, s, m, l, x
        epochs=50,
        batch_size=1
    )
    
    # 测试模型
    test_image = "data/YOLO/rawdata/images/frame_7.jpg"
    prediction = predict_segment(model, test_image)
    
    # 评估模型
    metrics = evaluate_model(model, trainer.val_dir)
    print("Validation Metrics:", metrics)