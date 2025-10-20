import socket
import struct

def receive_imu():
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5000))
    
    print("等待接收数据...")
    
    while True:
        try:
            # 接收数据
            data, addr = sock.recvfrom(1024)
            
            # 解包数据 - 只接收加速度数据
            x, y, z = struct.unpack('fff', data)
            
            print(f"X={x:.2f} Y={y:.2f} Z={z:.2f}")
            
        except Exception as e:
            print("错误:", e)

if __name__ == '__main__':
    receive_imu()