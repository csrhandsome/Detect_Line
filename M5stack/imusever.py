from m5stack import *
from m5ui import *
import imu
import json
import machine
import struct

class IMUSerial:
    def __init__(self, tx=1, rx=3, baudrate=115200):
        self.imu0 = imu.IMU()
        self.uart = machine.UART(1, tx=tx, rx=rx)
        self.uart.init(baudrate, bits=8, parity=None, stop=1)
        
    def send_data(self):
        while True:
            # 获取IMU数据
            x, y, z = self.imu0.acceleration
            
            # 打包数据
            data = struct.pack('fff', x, y, z)
            
            # 发送数据
            self.uart.write(data)
            
            wait_ms(10)  # 控制发送频率

if __name__ == '__main__':
    # 启动串口传输
    imu_serial = IMUSerial()
    imu_serial.send_data()