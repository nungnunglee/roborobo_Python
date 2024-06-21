import cv2
import numpy as np
from moveFunc import *

# 색상 무게 중심 반환
def yellow_line(frame):

    # 영상을 HSV로 변환
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 노란색으로 간주할 색상에 범위
    upper = np.array([40, 255, 255])
    lower = np.array([10, 0, 0])

    # 색상의 위치 마스크
    mask = cv2.inRange(hsv, lower, upper)

    cv2.imshow("mask", mask)
    # cv2.imshow("hsv", hsv)
    #
    # cv2.imshow("h", hsv[:, :, 0])
    # cv2.imshow("s", hsv[:, :, 1])
    # cv2.imshow("v", hsv[:, :, 2])

    # 마스크의 x 좌표들
    lx_array = np.where(mask[:, :30] == 255)[1]
    mx_array = np.where(mask[:, 30:290] == 255)[1]
    rx_array = np.where(mask[:, 290:] == 255)[1]

    # 영상에 노란색이 있다면
    if len(mx_array) > 10:
        # x 좌표의 평균 값을 반환
        mx = mx_array.mean() + 30

        cv2.circle(frame, (int(mx), 120), 5, (0, 0, 255), -1)
        cv2.imshow("circlr", frame)

        if len(lx_array) > 10:
            # x 좌표의 평균 값을 반환
            lx = lx_array.mean()
            cv2.circle(frame, (int(lx), 120), 5, (0, 255, 0), -1)
        else:
            lx = None

        if len(rx_array) > 10:
            # x 좌표의 평균 값을 반환
            rx = rx_array.mean() + 290
            cv2.circle(frame, (int(rx), 120), 5, (255, 0, 0), -1)
        else:
            rx = None

        cv2.imshow("circlr", frame)
        return (lx, mx, rx)
    else:
        # 노란색이 없으면 None 반환
        return None

momentum = True

# 노란색을 선으로 인식하고 찾아가는 함수
def line_action(rs, frame, sensor, params):

    global momentum

    # 영상에서 노란색의 무게중심 가져오기
    result = yellow_line(frame)

    if result is None:
        # 못 찾으면 일단 왼쪽으로 회전
        if momentum:
            turn(rs, 15)
        else:
            turn(rs, -15)
        return

    lx, mx, rx = result

    pad = 40

    # 영상의 중심을 기준으로 무게 중심이 치우치는 방향으로 회전
    if mx < 160 - pad or lx is not None:
        momentum = False
        if lx is None:
            smooth_turn(rs, -3)
        else:
            smooth_turn(rs, -8)
    elif 160 + pad < mx or rx is not None:
        momentum = True
        if rx is None:
            smooth_turn(rs, 3)
        else:
            smooth_turn(rs, 8)
    else:
        # 치우치지 않을 경우 직진
        forward(rs, 8)


if __name__ == '__main__':
    import os
    img_list = os.listdir('img')
    for img in img_list:
        img = cv2.imread('img/'+img)
        print(yellow_line(img))
        cv2.waitKey(0)