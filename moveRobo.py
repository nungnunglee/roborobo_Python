from RobokitRS import *
from time import sleep
import keyboard
from moveFunc import *
from threading import Thread
import queue
from testcam import *
import cv2

def move_robo(action, *prams):
    q = queue.Queue()

    rs = RobokitRS.RobokitRS()

    # windows port number
    rs.port_open("COM5")

    # 초음파 센서 입력 버퍼 열기
    rs.sonar_begin(13)

    # 적외선 센서 입력 버퍼 열기 12: F, 2: B
    rs.set_pin_mode(12, RobokitRS.Modes.INPUT)
    rs.set_pin_mode(2, RobokitRS.Modes.INPUT)

    is_getting = False
    frame = np.zeros((240, 320, 3), np.uint8)
    thr = None

    while True:
        if keyboard.is_pressed('ESC'):
            rs.end()
            break

        new_frame = None

        # 초음파 센서로 거리를 받기
        distance = rs.sonar_read(13)
        ir_f, ir_b = rs.digital_reads([12, 2])

        if not is_getting:
            # 카메라 화면 numpy 로 받기
            thr = Thread(target=get_robo_image, args=(q,))
            thr.start()
            is_getting = True

        thr.join(0.5)

        if thr.is_alive():
            print("can not get img")
        else:
            is_getting = False
            new_frame = q.get()

        if not is_getting:
            frame = new_frame

        cv2.imshow("frame", frame)

        action(rs, frame, (distance, ir_f, ir_b), prams)

        cv2.waitKey(1)


def goo(rs, frame, sensor, prams):
    cv2.imshow("action", frame)
    print("sensor", sensor)
    print("prams", prams)
    if 30 < sensor[0]:
        forward(rs, 15)
    else:
        forward(rs, 0)

if __name__ == '__main__':
    move_robo(goo, 1, 2, 3)
