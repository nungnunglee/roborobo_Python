import cv2
import numpy as np

import moveFunc


def get_line(src):
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gau = cv2.GaussianBlur(gray, (5, 5), 0)

    can = cv2.Canny(gau, 50, 150)

    mask = np.zeros_like(can)
    mask[2*mask.shape[0]//3:, :] = 255
    edges = cv2.bitwise_and(can, mask)

    # 직선 성분 검출
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180., 10, minLineLength=0, maxLineGap=5)

    # 컬러 영상으로 변경 (영상에 빨간 직선을 그리기 위해)
    dst = cv2.cvtColor(can, cv2.COLOR_GRAY2BGR)

    if lines is None:  # 라인 정보를 받았으면
        return

    rpts, lpts = [], []

    for i in range(lines.shape[0]):
        pt1 = (lines[i][0][0], lines[i][0][1])  # 시작점 좌표 x,y
        pt2 = (lines[i][0][2], lines[i][0][3])  # 끝점 좌표, 가운데는 무조건 0
        if (lines[i][0][0] + lines[i][0][2]) / 2 < can.shape[1] / 2:
            lpts.append(lines[i][0])
            cv2.line(dst, pt1, pt2, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            rpts.append(lines[i][0])
            cv2.line(dst, pt1, pt2, (255, 0, 0), 2, cv2.LINE_AA)

    r_pts = np.array(rpts)
    l_pts = np.array(lpts)

    r_line = r_pts.mean(0, dtype=np.int32)
    l_line = l_pts.mean(0, dtype=np.int32)

    r_angle = (r_line[3] - r_line[1]) / (r_line[2] - r_line[0])
    l_angle = (l_line[3] - l_line[1]) / (l_line[2] - l_line[0])
    return r_angle, l_angle


def line_tracking(src):
    rangle, langle = get_line(src)
    pad = 0.1
    if rangle + langle < -pad:
        moveFunc.turn(-5)
    elif pad < rangle + langle:
        moveFunc.turn(5)
    else:
        moveFunc.forward(5)

if __name__ == '__main__':
    TEST_IMG_PATH = "data/road.jpg"
    img = cv2.imread(TEST_IMG_PATH)



