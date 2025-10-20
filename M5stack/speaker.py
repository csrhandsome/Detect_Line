from m5stack import *
from m5stack_ui import *
from uiflow import *
import imu
import network
import socket
import struct
import math

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

def get_pitch_roll(acc_x, acc_y, acc_z):
    # 计算俯仰角和横滚角
    pitch = math.atan2(acc_x, math.sqrt(acc_y * acc_y + acc_z * acc_z)) * 180 / math.pi
    roll = math.atan2(acc_y, math.sqrt(acc_x * acc_x + acc_z * acc_z)) * 180 / math.pi
    return pitch, roll

def play_sound_by_angle(pitch, roll):
    # 根据角度计算频率（范围从500Hz到2000Hz）
    freq = 500 + abs(pitch + roll) * 10
    freq = min(2000, max(500, freq))  # 限制频率范围
    
    # 如果角度变化超过阈值才发声
    if abs(pitch) > 20 or abs(roll) > 20:
        speaker.playTone(freq, 50)  # 播放指定频率的声音50ms

while True:
    try:
        # 获取IMU数据
        acc_x, acc_y, acc_z = imu0.acceleration
        gyro_x, gyro_y, gyro_z = imu0.gyro
        
        # 计算角度
        pitch, roll = get_pitch_roll(acc_x, acc_y, acc_z)
        
        # 根据角度发声
        play_sound_by_angle(pitch, roll)
        
        # 打包数据
        data = struct.pack('fff', acc_x, acc_y, acc_z)
        
        # 更新显示
        label_acc.set_text('ACC: X={:.2f} Y={:.2f} Z={:.2f}'.format(acc_x, acc_y, acc_z))
        label_gyro.set_text('GYRO: X={:.2f} Y={:.2f} Z={:.2f}'.format(gyro_x, gyro_y, gyro_z))
        
        # 发送数据
        sock.sendto(data, (UDP_IP, UDP_PORT))
        label_status.set_text('Status: Sending')
        
    except Exception as e:
        label_status.set_text('Error: ' + str(e))
        
    wait_ms(10)  # 发送间隔