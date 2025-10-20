from YOLO.train.runner import YOLO_Runner
def eval(trainer):
    # 初始化训练器
    trainer = YOLO_Runner(data_dir="data/YOLO/rawdata",output_dir="data/YOLO/output")
    # 测试模型
    test_image = "data/YOLO/rawdata/images/frame_7.jpg"
    prediction = trainer.predict_segment(test_image)
    
    # 评估模型
    metrics = trainer.evaluate_model(trainer.val_dir)
    print("Validation Metrics:", metrics)