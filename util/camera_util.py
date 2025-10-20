import cv2
import socket
import pickle
import struct
import time
import numpy as np
def test_camera(video_path='data/YOLO/video/running.mp4'):   
    # Open the video file
    # video_path = "path/to/video.mp4"
    cap = cv2.VideoCapture(0)
    
    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        # Display the annotated frame
        cv2.imshow("camera", frame)
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

def receive_video():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', 8485))
        server_socket.listen(5)
        print("等待连接...")
        
        client_socket, addr = server_socket.accept()
        print(f"连接成功: {addr}")
        
        data = b""
        payload_size = struct.calcsize("Q")
        
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4*1024)
                if not packet:
                    break
                data += packet
            
            if not data:
                break
                
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            
            while len(data) < msg_size:
                data += client_socket.recv(4*1024)
            
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            # 解码图像
            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is not None:
                cv2.imshow('接收视频', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"错误: {e}")
    finally:
        print("关闭连接")
        client_socket.close()
        server_socket.close()
        cv2.destroyAllWindows()

def server_test():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('0.0.0.0', 8485))
        print("绑定成功")
        server.listen(5)
        print("等待连接...")
        
        while True:
            client, addr = server.accept()
            print(f"连接成功：{addr}")
            data = client.recv(1024)
            print(f"收到数据：{data.decode()}")
    except Exception as e:
        print(f"错误：{e}")
    finally:
        server.close()


if __name__ == '__main__':
    # test_camera()    
    #server_test()           
    receive_video()
