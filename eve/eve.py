import uiautomator2 as u2
import cv2
import numpy as np
import random
import time
import subprocess
import threading
import sys

# 音频支持 - 跨平台兼容性
try:
    import winsound  # Windows平台
    def play_beep():
        """播放beep声（Windows）"""
        try:
            winsound.Beep(500, 1000)
        except:
            print("音频提示不可用")
except ImportError:
    def play_beep():
        """播放beep声（非Windows平台）"""
        print("音频提示 (哔)")

class EVEScript:
    def __init__(self, device_address, device_remark='', match_threshold=0.9):
        self.device_address = device_address
        self.device_remark = device_remark
        self.d = None
        self.running = False
        self.thread = None
        self.debug_mode = False  # 调试模式，默认关闭
        self.match_threshold = match_threshold  # 模板匹配阈值
        
        # 初始化红白图
        self.img1 = cv2.imread('./1.png')
        self.img1grey = cv2.cvtColor(self.img1, cv2.COLOR_BGR2GRAY)

        self.img2 = cv2.imread('./2.png')
        self.img2grey = cv2.cvtColor(self.img2, cv2.COLOR_BGR2GRAY)

        self.img3 = cv2.imread('./3.png')
        self.img3grey = cv2.cvtColor(self.img3, cv2.COLOR_BGR2GRAY)

        self.imgOverView = cv2.imread('./overview.png')
        self.imgOverViewgrey = cv2.cvtColor(self.imgOverView, cv2.COLOR_BGR2GRAY)
        
        self.imgVisitor = cv2.imread('./visitor.png')
        self.imgVisitorgrey = cv2.cvtColor(self.imgVisitor, cv2.COLOR_BGR2GRAY)

    def log(self, message, is_important=False):
        """统一的日志输出方法
        :param message: 日志消息
        :param is_important: 是否为重要日志(即使调试关闭也会显示)
        """
        if self.debug_mode or is_important:
            remark_info = f" - {self.device_remark}" if self.device_remark else ""
            print(f'{self.device_address}{remark_info}: {message}')

    def connect_device(self):
        """连接设备"""
        try:
            self.d = u2.connect(self.device_address)
            remark_info = f" - {self.device_remark}" if self.device_remark else ""
            self.log(f"设备{remark_info}连接成功", is_important=True)
            self.log(str(self.d.info))
            return True
        except Exception as e:
            self.log(f"连接设备失败: {e}", is_important=True)
            return False

    def work(self):
        """工作循环"""
        if not self.d:
            return False
            
        #循环截图 对比
        image = self.d.screenshot(format='opencv')
#        cv2.imwrite('screenshot.jpg', image)
#        imgmain = cv2.imread('screenshot.jpg')
        imgmain = image  # 使用截图作为imgmain
        imgmaingrey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        res1 = cv2.matchTemplate(imgmaingrey, self.img1grey, cv2.TM_CCOEFF_NORMED)
        loc1 = np.where(res1 >= self.match_threshold)
        pt1 = list(zip(*loc1[::-1]))

        res2 = cv2.matchTemplate(imgmaingrey, self.img2grey, cv2.TM_CCOEFF_NORMED)
        loc2 = np.where(res2 >= self.match_threshold)
        pt2 = list(zip(*loc2[::-1]))

        res3 = cv2.matchTemplate(imgmaingrey, self.img3grey, cv2.TM_CCOEFF_NORMED)
        loc3 = np.where(res3 >= self.match_threshold)
        pt3 = list(zip(*loc3[::-1]))

        result = 0
        if len(pt1) > 0:
            result = result +1
        if len(pt2) > 0:
            result = result +1
        if len(pt3) > 0:
            result = result +1

        #回站黑屏处理
        isBlack = self.isBlackScreen(imgmain)
        if isBlack:
            time.sleep(20)
            return False
            
        #判断是否在站内
        inStation = self.isInStation(imgmaingrey)
        if inStation:
            self.log("蹲站中", is_important=True)
            time.sleep(60)
            return False

        #打开总览
        oveview = cv2.matchTemplate(imgmaingrey, self.imgOverViewgrey, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(oveview)
        if max_val > 0.8:
            overviewX = max_loc[0]
            if overviewX > 1100:
                ran = random.randint(0, 15)
                self.d.click(max_loc[0] + ran, max_loc[1] + ran)
                time.sleep(2)

        #都匹配上result为3 不用跑 小于3就跑
        if result < 3:
            self.log("跑", is_important=True)
            play_beep()  # 使用跨平台音频播放
            return True
        else:
            # "没事"日志只在调试模式显示
            self.log("没事")  # 普通日志，调试模式才显示
            return False

    def isBlackScreen(self, imgmain):
        """检测黑屏"""
        posi1 = imgmain[0,0]
        posi2 = imgmain[100,0]
        posi3 = imgmain[0,100]
        posi4 = imgmain[100,100]
        black_threshold = 20

        isBlack1 = all(value < black_threshold for value in posi1)
        isBlack2 = all(value < black_threshold for value in posi2)
        isBlack3 = all(value < black_threshold for value in posi3)
        isBlack4 = all(value < black_threshold for value in posi4)

        all_black = isBlack1 and isBlack2 and isBlack3 and isBlack4

        if all_black == True:
            self.log("黑屏", is_important=True)
            return True
        return False
        
    def isInStation(self, imgmaingrey):
        """检测是否在空间站内"""
        res1 = cv2.matchTemplate(imgmaingrey, self.imgVisitorgrey, cv2.TM_CCOEFF_NORMED)
        loc1 = np.where(res1 >= self.match_threshold)
        pt1 = list(zip(*loc1[::-1]))
        
        if len(pt1) > 0:
            return True
        return False

    def run_miner(self):
        """运行挖矿操作"""
        ran = random.randint(-5, 5)
        #导航 左侧导航
        #self.d.click(30 + ran, 200 + ran)
        #右侧军堡
        self.d.click(1095 + ran, 83 + ran)
        time.sleep(1)
        self.d.click(831 + ran, 91 + ran)
        time.sleep(1.5)
        #皮球
        self.d.click(1077 + ran, 650 + ran)
        time.sleep(.3)
        #皮球
        self.d.click(1149 + ran, 650 + ran)
        time.sleep(.3)
        #皮球
        self.d.click(1222 + ran, 650 + ran)
        time.sleep(.3)

    def run_battle_ship(self):
        """运行战列舰操作"""
        ran = random.randint(-5, 5)
        #导航 左侧导航
        #self.d.click(30 + ran, 200 + ran)
        #右侧军堡
        self.d.click(1095 + ran, 83 + ran)
        time.sleep(1)
        self.d.click(831 + ran, 91 + ran)
        time.sleep(1.5)

    def run_script(self):
        """主运行循环"""
        try:
            if not self.connect_device():
                return
                
            self.running = True
            hasRun = False
            while self.running:
                try:
                    hasRun = self.work()
                    if hasRun == True:
                        self.run_battle_ship()
                        for _ in range(30):  # 将长sleep拆分为短sleep
                            if not self.running:  # 检查停止标志
                                break
                            time.sleep(1)
                    for _ in range(3):  # 将1.5秒拆分为3个0.5秒
                        if not self.running:
                            break
                        time.sleep(0.5)
                except Exception as e:
                    # 错误日志总是显示
                    self.log(f"执行错误 - {e}", is_important=True)
                    time.sleep(5)  # 出错后等待一段时间再重试
        except Exception as e:
            # 错误日志总是显示
            self.log(f"脚本启动失败 - {e}", is_important=True)

    def start(self):
        """启动脚本"""
        self.thread = threading.Thread(target=self.run_script, 
                                      name=f"EVE-Script-{self.device_address}")
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """停止脚本"""
        self.running = False
        if self.thread and self.thread.is_alive():
            # 使用非阻塞方式，不等待线程结束
            # 线程会在下一次循环检查running标志时自动退出
            pass  # 让线程自然结束，避免阻塞UI

def main():
    """独立运行时的主函数"""
    script = EVEScript('127.0.0.1:16384')
    try:
        script.run_script()
    except KeyboardInterrupt:
        script.stop()

if __name__ == "__main__":
    main()
