import cv2
import os
from ultralytics import YOLO
from pathlib import Path
import subprocess
import socket
import struct
import numpy as np


def video2frames(video_path, frame_num):
    video_path = str(Path(video_path))  # 确保路径无误
    # 打开视频文件
    # 根据select_cap函数选出的backend
    cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("Failed to open video with CAP_FFMPEG")
    # 获取视频的总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 如果要每一帧都截取则加上这个 frame_num = total_frames
    step = 20  # 采样间隔
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


def frames2jpg(frames, output_dir="data/YOLO/rawdata/images"):
    for i, frame in enumerate(frames):
        cv2.imwrite(os.path.join(output_dir, f"frame_{i}.jpg"), frame)


def normal_YOLO_through_camera(
    model_name="YOLO/model/yolo11n-seg.pt", video_path="data/YOLO/video/running.mp4"
):
    # Load the YOLO11 model
    model = YOLO(model_name)

    # Open the video file
    # video_path = "path/to/video.mp4"
    cap = cv2.VideoCapture(video_path)

    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Run YOLO11 tracking on the frame, persisting tracks between frames
            results = model.track(
                frame,
                persist=True,
                show_boxes=False,  # 新参数名称：不显示边界框
                show_labels=False,  # 新参数名称：不显示标签
                show_conf=False,  # 新参数名称：不显示置信度
            )

            # 只使用基本参数
            annotated_frame = results[0].plot(
                boxes=False,
                labels=False,
                conf=False,
                masks=True,  # 只显示分割mask
                line_width=2,  # 增加线条宽度
            )

            # Display the annotated frame
            cv2.imshow("Line segment", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()


def labelme2mask(json_dir="data/YOLO/rawdata/json"):
    """
    写一个python的脚本,不断的在命令行里面输入labelme_json_to_dataset json_file,这样将所有的json文件转换为对应的dataset格式
    """
    # 设置JSON文件夹路径
    json_dir = Path(json_dir)

    # 处理所有json文件
    for json_file in json_dir.glob("*.json"):
        cmd = ["labelme_json_to_dataset", str(json_file)]
        print(f"Processing {json_file.name}...")
        subprocess.run(cmd)
        print(f"Completed {json_file.name}")

    print("All files processed!")


def receive_video_with_socket(use_raspberrypi=False):
    # Load the YOLO11 model
    model_name = "runs/segment/train/weights/best.pt"
    model = YOLO(model_name)

    if use_raspberrypi:
        # 使用树莓派socket接收视频
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind(("0.0.0.0", 8485))
            server_socket.listen(5)
            print("等待连接...")

            client_socket, addr = server_socket.accept()
            print(f"连接成功: {addr}")

            data = b""
            payload_size = struct.calcsize("Q")

            while True:
                while len(data) < payload_size:
                    packet = client_socket.recv(4 * 1024)
                    if not packet:
                        break
                    data += packet

                if not data:
                    break

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(4 * 1024)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                # 解码图像
                frame = cv2.imdecode(
                    np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR
                )
                if frame is not None:
                    # Run YOLO11 tracking on the frame, persisting tracks between frames
                    results = model.track(
                        frame,
                        persist=True,
                        show_boxes=False,  # 新参数名称：不显示边界框
                        show_labels=False,  # 新参数名称：不显示标签
                        show_conf=False,  # 新参数名称：不显示置信度
                    )

                    # 只使用基本参数
                    annotated_frame = results[0].plot(
                        boxes=False,
                        labels=False,
                        conf=False,
                        masks=True,  # 只显示分割mask
                    )

                    # Display the annotated frame
                    cv2.imshow("Line segment", annotated_frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

        except Exception as e:
            print(f"错误: {e}")
        finally:
            print("关闭连接")
            client_socket.close()
            server_socket.close()
            cv2.destroyAllWindows()
    else:
        # 使用本地摄像头
        cap = cv2.VideoCapture(2)

        try:
            print("使用本地摄像头...")

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("无法读取摄像头画面")
                    break

                # Run YOLO11 tracking on the frame, persisting tracks between frames
                results = model.track(
                    frame,
                    persist=True,
                    show_boxes=False,  # 新参数名称：不显示边界框
                    show_labels=False,  # 新参数名称：不显示标签
                    show_conf=False,  # 新参数名称：不显示置信度
                )

                # 只使用基本参数
                annotated_frame = results[0].plot(
                    boxes=False, labels=False, conf=False, masks=True  # 只显示分割mask
                )

                # Display the annotated frame
                cv2.imshow("Line segment", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        except Exception as e:
            print(f"错误: {e}")
        finally:
            print("关闭摄像头")
            cap.release()
            cv2.destroyAllWindows()
