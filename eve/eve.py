import uiautomator2 as u2
import cv2
import numpy as np
import random
import time

# 连接模拟器
d = u2.connect('emulator-5554')
#print(d.info)

# 初始化红白图
img1 = cv2.imread('./1.png')
img1grey = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

img2 = cv2.imread('./2.png')
img2grey = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

img3 = cv2.imread('./3.png')
img3grey = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)


def work():
	#循环截图 对比
	image = d.screenshot(format='opencv')
	cv2.imwrite('screenshot.jpg', image)
	imgmain = cv2.imread('screenshot.jpg')
	imgmaingrey = cv2.cvtColor(imgmain, cv2.COLOR_BGR2GRAY)

	res1 = cv2.matchTemplate(imgmaingrey, img1grey, cv2.TM_CCOEFF_NORMED)
	loc1 = np.where(res1 >= 0.9)
	pt1 = list(zip(*loc1[::-1]))

	res2 = cv2.matchTemplate(imgmaingrey, img2grey, cv2.TM_CCOEFF_NORMED)
	loc2 = np.where(res2 >= 0.9)
	pt2 = list(zip(*loc2[::-1]))

	res3 = cv2.matchTemplate(imgmaingrey, img3grey, cv2.TM_CCOEFF_NORMED)
	loc3 = np.where(res3 >= 0.9)
	pt3 = list(zip(*loc3[::-1]))

#	for pt in zip(*loc1[::-1]):
#		print(pt[0], pt[1])
#	for pt in zip(*loc2[::-1]):
#		print(pt[0], pt[1])
#	for pt in zip(*loc3[::-1]):
#		print(pt[0], pt[1])

	result = 0
	if len(pt1) > 0:
		result = result +1
	if len(pt2) > 0:
		result = result +1
	if len(pt3) > 0:
		result = result +1

	#都匹配上result为3 不用跑 小于3就跑
	if result < 3:
		print('跑')
		run_miner()
		return True
	else:
		print('没事')
		return False

def run_miner():
	ran = random.randint(-5, 5)
	#导航
	d.click(30 + ran, 200 + ran)
	time.sleep(1)
	#皮球
	d.click(1077 + ran, 650 + ran)
	time.sleep(.3)
	#皮球
	d.click(1149 + ran, 650 + ran)
	time.sleep(.3)
	#皮球
	d.click(1222 + ran, 650 + ran)
	time.sleep(.3)


hasRun = False
while not hasRun:
	hasRun = work()
	time.sleep(1)
