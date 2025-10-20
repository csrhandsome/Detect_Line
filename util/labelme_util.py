import subprocess
from pathlib import Path
def labelme2mask(data_dir="data/YOLO/rawdata"):
    """
    写一个python的脚本,不断的在命令行里面输入labelme_json_to_dataset json_file,这样将所有的json文件转换为对应的dataset格式
    仅仅在linux上面用
    """
    # 设置JSON文件夹路径
    json_dir = Path(data_dir) / "json"
    mask_dir = Path(data_dir) / "labels"
    # 处理所有json文件
    for json_file in json_dir.glob("*.json"):
        # cmd运行labelme_json_to_dataset命令
        cmd = ["labelme_json_to_dataset", str(json_file)]
        print(f"Processing {json_file.name}...")
        subprocess.run(cmd)
        print(f"Completed {json_file.name}")
        
        # cmd移动label.png文件到mask目录
        json_name = json_file.stem  # 获取不带扩展名的文件名
        mask_file = json_dir / f"{json_name}_json" / "label.png"
        if mask_file.exists():
            # 移动并重命名label.png，使用原json文件名
            subprocess.run(["mv", str(mask_file), str(mask_dir / f"{json_name}.png")])
        # cmd删除文件夹
        json_folder = json_dir / f"{json_name}_json"
        if json_folder.exists():
            subprocess.run(["rm", "-rf", str(json_folder)])
    print("All files processed!")
