import cv2
import numpy as np
from moveFunc import *

def yellow_line(frame):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    upper = np.array([40, 140, 255])
    lower = np.array([10, 50, 0])

    mask = cv2.inRange(hsv, lower, upper)

    cv2.imshow("mask", mask)

    x_array = np.where(mask == 255)[1]

    if len(x_array) != 0:
        mx = x_array.mean()
        cv2.circle(frame, (int(mx), 120), 5, (0, 0, 255), -1)
        cv2.imshow("circlr", frame)
        return mx
    else:
        return None


def line_action(rs, frame, sensor, params):

    mx = yellow_line(frame)

    if mx is None:
        turn(rs, -15)
        return

    pad = 50

    if mx < 160 - pad:
        turn(rs, -4)
    elif 160 + pad < mx:
        turn(rs, 4)
    else:
        forward(rs, 2)


