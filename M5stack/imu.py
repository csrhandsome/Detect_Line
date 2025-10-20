from m5stack import *
from m5ui import *
from uiflow import *
import imu
import time

class IMUHandler:
    def __init__(self, smooth_factor=0.1, samples=5):
        self.imu0 = imu.IMU()
        self.smooth_factor = smooth_factor
        self.samples = samples
        # 平滑后的数据
        self.smooth_x = 0
        self.smooth_y = 0
        self.smooth_z = 0
        # 校准偏移值
        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        setScreenColor(0x111111)
        self.acc_x = M5TextBox(15, 10, "acc_x:", lcd.FONT_DejaVu18, 0xFFFFFF)
        self.acc_y = M5TextBox(15, 40, "acc_y:", lcd.FONT_DejaVu18, 0xFFFFFF)
        self.acc_z = M5TextBox(15, 70, "acc_z:", lcd.FONT_DejaVu18, 0xFFFFFF)
        self.status = M5TextBox(15, 100, "", lcd.FONT_DejaVu18, 0x00FF00)
        
    def calibrate(self):
        """校准IMU"""
        self.status.setText("Calibrating...")
        sum_x = sum_y = sum_z = 0
        
        # 采集多个样本求平均
        for _ in range(self.samples):
            x, y, z = self.imu0.acceleration
            sum_x += x
            sum_y += y
            sum_z += z
            wait_ms(50)
            
        # 计算偏移值
        self.offset_x = sum_x / self.samples
        self.offset_y = sum_y / self.samples
        self.offset_z = sum_z / self.samples - 1  # 减去重力加速度
        
        self.status.setText("Calibration done")
        wait_ms(1000)
        self.status.setText("")
        
    def smooth_data(self, new_x, new_y, new_z):
        """使用低通滤波平滑数据"""
        self.smooth_x = self.smooth_factor * (new_x - self.offset_x) + (1 - self.smooth_factor) * self.smooth_x
        self.smooth_y = self.smooth_factor * (new_y - self.offset_y) + (1 - self.smooth_factor) * self.smooth_y
        self.smooth_z = self.smooth_factor * (new_z - self.offset_z) + (1 - self.smooth_factor) * self.smooth_z
        
    def update_display(self):
        """更新显示"""
        self.acc_x.setText("acc_x: %.3f" % self.smooth_x)
        self.acc_y.setText("acc_y: %.3f" % self.smooth_y)
        self.acc_z.setText("acc_z: %.3f" % self.smooth_z)
        
    def detect_motion(self):
        """检测运动状态"""
        magnitude = (self.smooth_x**2 + self.smooth_y**2 + self.smooth_z**2)**0.5
        if magnitude > 0.5:  # 可调整阈值
            self.status.setText("Motion detected!")
            self.status.setColor(0xFF0000)
        else:
            self.status.setText("Stable")
            self.status.setColor(0x00FF00)
            
    def run(self):
        """主循环"""
        last_update = time.ticks_ms()
        update_interval = 100  # 更新间隔(ms)
        
        # 首次校准
        self.calibrate()
        
        while True:
            current_time = time.ticks_ms()
            
            # 按键处理
            if btnA.wasPressed():  # A键触发校准
                self.calibrate()
                
            if btnB.wasPressed():  # B键切换显示模式
                self.toggle_display_mode()
                
            # 定时更新数据
            if current_time - last_update >= update_interval:
                x, y, z = self.imu0.acceleration
                self.smooth_data(x, y, z)
                self.update_display()
                self.detect_motion()
                last_update = current_time
                
            wait_ms(10)  # 降低CPU使用率

if __name__ == '__main__':
    # 创建并运行IMU处理器
    imu_handler = IMUHandler()
    imu_handler.run()