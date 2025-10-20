from m5stack import *
from m5stack_ui import *
from uiflow import *
import imu
import network
import socket
import json
import time



# UDP配置
UDP_IP = "192.168.253.69"  
UDP_PORT = 5000

# 初始化屏幕
screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0xFFFFFF)

# 初始化IMU
imu0 = imu.IMU()

# 初始化显示组件
label_imu = M5Label('IMU Data:', x=20, y=10, color=0x000, font=FONT_MONT_18, parent=None)
label_acc = M5Label('ACC:', x=20, y=40, color=0x000, font=FONT_MONT_18, parent=None)
label_gyro = M5Label('GYRO:', x=20, y=70, color=0x000, font=FONT_MONT_18, parent=None)
label_status = M5Label('Status:', x=20, y=100, color=0x000, font=FONT_MONT_18, parent=None)

# 创建UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # 获取IMU数据
    acc_x, acc_y, acc_z = imu0.acceleration
    gyro_x, gyro_y, gyro_z = imu0.gyro
    
    # 打包数据 - 只发送加速度数据
    data = struct.pack('fff', acc_x, acc_y, acc_z)
    
    # 更新显示
    label_acc.set_text('ACC: X={:.2f} Y={:.2f} Z={:.2f}'.format(acc_x, acc_y, acc_z))
    label_gyro.set_text('GYRO: X={:.2f} Y={:.2f} Z={:.2f}'.format(gyro_x, gyro_y, gyro_z))
    
    # 直接发送打包后的数据，不需要json
    sock.sendto(data, (UDP_IP, UDP_PORT))
    label_status.set_text('Status: Sending')
    
            
        