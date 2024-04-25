import cv2
import numpy as np
import testcam
import moveFunc
from RobokitRS import *
import keyboard
import time
from threading import Thread
import queue

TEST_IMG_PATH = "C:/Users/dilab/Pictures/A019 - 20200609_122330.jpg"
color = (0, 0, 0)
q = queue.Queue()


def mouse_event(event, x, y, flags, param):
    global color
    if event == cv2.EVENT_LBUTTONDOWN:
        target_color = param[y, x]
        print("BGR:", target_color)
        color = target_color
    print("point color:", param[y, x])


def find_color(frame, color, padding = 10):
    # frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    upper = cv2.addWeighted(color, 1, padding, 1, 0)
    lower = cv2.addWeighted(color, 1, padding, -1, 0)

    # 색상 위치가 255인 mask
    mask = cv2.inRange(frame, lower, upper)
    y_arr, x_arr = np.where(mask == 255)

    if len(x_arr) == 0:
        # 못 찾으면 None 반환
        return None, None

    # 찾으면 x, y 좌표 반환
    return int(x_arr.mean()), int(y_arr.mean())


def find_test():
    global color
    img = cv2.imread(TEST_IMG_PATH)
    re_img = cv2.resize(img, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)
    cv2.imshow("img", re_img)
    cv2.setMouseCallback("img", mouse_event, re_img)

    x, y = find_color(re_img, color)
    print("(x, y):", (x, y), "color:", re_img[y, x])
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def follow_color():
    global color

    rs = RobokitRS.RobokitRS()

    # windows port number
    rs.port_open("COM5")

    # 초음파 센서 입력 버퍼 열기
    rs.sonar_begin(13)

    # 적외선 센서 입력 버퍼 열기 12: F, 2: B
    rs.set_pin_mode(12, RobokitRS.Modes.INPUT)
    rs.set_pin_mode(2, RobokitRS.Modes.INPUT)

    is_getting = False

    Frame = np.zeros((240, 320, 3), np.uint8)
    cx, cy = 160, 120

    while True:
        if keyboard.is_pressed('ESC'):
            rs.end()
            break

        newFrame = None
        x, y = None, None

        # 초음파 센서로 거리를 받기
        distance = rs.sonar_read(13)

        if not is_getting:
            # 카메라 화면 numpy 로 받기
            thr = Thread(target=testcam.get_robo_image, args=(q,))
            thr.start()
            is_getting = True

        thr.join(0.5)
        if thr.is_alive():
            print("can not get img")
        else:
            is_getting = False
            newFrame = q.get()

            # 색상에 중심 좌표
            x, y = find_color(newFrame, color)

        # 못 찾을 시 중심 좌표로
        if x is None:
            x, y = cx, cy

        if not is_getting:
            Frame = newFrame

        # 화면 띄우고 마우스 이벤트 연결
        cir_frame = cv2.circle(Frame.copy(), (x, y), 5, (0, 0, 255), -1)
        cv2.imshow('frame', cir_frame)
        cv2.setMouseCallback("frame", mouse_event, Frame)

        if x < cx - 10:
            moveFunc.right(rs, 5)
        elif cx + 10 < x:
            moveFunc.right(rs, -5)
        elif distance >= 30:
            moveFunc.forward(rs, 15)
        elif distance < 20:
            moveFunc.forward(rs, -15)
        else:
            moveFunc.right(rs, 0)

        cv2.waitKey(1)


if __name__ == '__main__':
    follow_color()
