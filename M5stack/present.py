from m5stack import *
from m5stack_ui import *
from uiflow import *
import MicrophonePDM as MIC
import imu

screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0xFFFFFF)

# 初始化IMU
imu0 = imu.IMU()

# 麦克风相关组件
label0 = M5Label('label0', x=20, y=30, color=0x000, font=FONT_MONT_18, parent=None)
label1 = M5Label('Volume', x=20, y=10, color=0x000, font=FONT_MONT_18, parent=None)


# IMU相关组件
label_imu = M5Label('IMU Data:', x=20, y=80, color=0x000, font=FONT_MONT_18, parent=None)
label_acc_x = M5Label('ACC_X:', x=20, y=100, color=0x000, font=FONT_MONT_18, parent=None)
label_acc_y = M5Label('ACC_Y:', x=20, y=120, color=0x000, font=FONT_MONT_18, parent=None)
label_acc_z = M5Label('ACC_Z:', x=20, y=140, color=0x000, font=FONT_MONT_18, parent=None)
label_gyro_x = M5Label('GYRO_X:', x=20, y=160, color=0x000, font=FONT_MONT_18, parent=None)
label_gyro_y = M5Label('GYRO_Y:', x=20, y=180, color=0x000, font=FONT_MONT_18, parent=None)
label_gyro_z = M5Label('GYRO_Z:', x=20, y=200, color=0x000, font=FONT_MONT_18, parent=None)

# 初始化麦克风
MIC.begin(pin_ws=0, pin_data=34, sample_rate_hz=16000, buffer_length_ms=1000, block_length_ms=100)

def update_imu_data():
    # 获取加速度数据
    acc_x, acc_y, acc_z = imu0.acceleration
    # 获取陀螺仪数据
    gyro_x, gyro_y, gyro_z = imu0.gyro
    
    # 更新显示
    label_acc_x.set_text('ACC_X: {:.2f}'.format(acc_x))
    label_acc_y.set_text('ACC_Y: {:.2f}'.format(acc_y))
    label_acc_z.set_text('ACC_Z: {:.2f}'.format(acc_z))
    label_gyro_x.set_text('GYRO_X: {:.2f}'.format(gyro_x))
    label_gyro_y.set_text('GYRO_Y: {:.2f}'.format(gyro_y))
    label_gyro_z.set_text('GYRO_Z: {:.2f}'.format(gyro_z))

while True:
    # 更新麦克风数据
    rms = MIC.getRMS()
    x = min(max(((rms - 1000) / 1500) * 280, 0), 280)
    label0.set_text(str(rms))
    
    # 更新IMU数据
    update_imu_data()
    
    wait_ms(2)