import serial
import struct
import time

class IMUReceiver:
    def __init__(self, port='COM3', baudrate=115200):  # 根据实际串口修改COM口
        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            print(f"成功打开串口 {port}")
        except Exception as e:
            print(f"打开串口失败: {e}")
            raise
        
    def receive_data(self):
        try:
            count = 0
            while True:
                # 等待接收完整的数据包(3个float = 12字节)
                if self.serial.in_waiting >= 12:
                    data = self.serial.read(12)
                    
                    # 解析数据
                    x, y, z = struct.unpack('fff', data)
                    
                    count += 1
                    if count % 100 == 0:  # 每100次打印一次
                        print(f"数据包 {count}: x={x:.3f}, y={y:.3f}, z={z:.3f}")
                    
                time.sleep(0.01)  # 控制接收频率
                
        except KeyboardInterrupt:
            print("\n用户停止程序")
        except Exception as e:
            print(f"接收错误: {e}")
        finally:
            self.close()
            
    def close(self):
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()
            print("串口已关闭")

def list_available_ports():
    """列出所有可用的串口"""
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("没有找到可用的串口")
        return
    
    print("\n可用的串口:")
    for port in ports:
        print(f"设备: {port.device}")
        print(f"描述: {port.description}")
        print(f"硬件ID: {port.hwid}\n")

if __name__ == "__main__":
    try:
        # 创建接收器实例
        receiver = IMUReceiver(port='COM3')
        print("开始接收数据...")
        # 开始接收数据
        receiver.receive_data()
    except Exception as e:
        print(f"程序错误: {e}")