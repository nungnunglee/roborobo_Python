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


def get_load_region(image: np.ndarray, inrange_upper: tuple = (40, 255, 255), inrange_lower: tuple = (10, 0, 10), canny_threshold: tuple = (100, 200), kernel_size: tuple = (5, 5), dilate_iterations: int = 1, erode_iterations: int = 1):
    """
    영상에서 길 영역을 찾아 반환하는 함수\n
    inRange 함수를 사용하여 색상 영역을 대충 찾아 fill point를 찾고, \n
    Canny로 엣지를 검출한 사진에 fill point로\n
    flood fill 함수를 사용하여 길 영역을 찾아 반환한다.\n
    Args:\n
        image: 영상\n
        inrange_upper: 길 영역 색상의 상한 값 (HSV)\n
        inrange_lower: 길 영역 색상의 하한 값 (HSV)\n
        canny_threshold: Canny 엣지 검출 임계값 (min, max)\n
        kernel_size: 커널 크기 (height, width)\n
        dilate_iterations: canny 팽창 반복 횟수\n
        erode_iterations: inrange mask 침식 반복 횟수\n
    Returns:\n
        filled_image: 길 영역 마스크
    """
    h, w = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, inrange_lower, inrange_upper)
    
    canny = cv2.Canny(image, canny_threshold[0], canny_threshold[1])

    kernel = np.ones(kernel_size, np.uint8)
    dilated_canny = cv2.dilate(canny, kernel, iterations=dilate_iterations)
    eroded_mask = cv2.erode(mask, kernel, iterations=erode_iterations)
    # eroded_mask = mask

    y_idx, x_idx = np.where(eroded_mask == 255)
    random_index = np.random.randint(0, len(y_idx))
    seed_point = (x_idx[random_index], y_idx[random_index])

    ff_mask = np.zeros((h + 2, w + 2), np.uint8)
    ff_mask[1:h+1, 1:w+1] = dilated_canny
    filled_image = np.zeros((h, w), np.uint8)

    cv2.floodFill(filled_image, ff_mask, seed_point, 255, 0, 0, cv2.FLOODFILL_FIXED_RANGE)

    return filled_image


if __name__ == '__main__':
    import os
    img_list = os.listdir('img')
    for img in img_list:
        img = cv2.imread('img/'+img)
        print(yellow_line(img))
        cv2.waitKey(0)