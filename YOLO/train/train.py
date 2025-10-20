from YOLO.train.runner import YOLO_Runner
def train(ismask=False):  
    # 初始化训练器
    trainer = YOLO_Runner(data_dir="data/YOLO/rawdata",output_dir="data/YOLO/output")
    # 准备数据集
    yaml_path = trainer.prepare_dataset(0, val_size=0.2)
    yaml_path = 'data/YOLO/output/data.yaml'
    # 训练模型
    results = trainer.train_yolo_seg(
        data_yaml_path=yaml_path,
        model_size='n',  # n, s, m, l, x
        epochs=100,
        batch_size=2
    )
    
    # 测试模型
    test_image = "data/YOLO/rawdata/images/frame_7.jpg"
    prediction = trainer.predict_segment(test_image)
    
    # 评估模型
    metrics = trainer.evaluate_model(trainer.val_dir)
    print("Validation Metrics:", metrics)