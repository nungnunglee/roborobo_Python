from RobokitRS import *
import numpy as np


# 모터 회전 방향은 f_list 에서 조절

def forward(rs: RobokitRS.RobokitRS, speed: int = 15):
    f_list = np.array([1, 0, 1, 0])
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)


def turn(rs: RobokitRS.RobokitRS, speed: int = 15):
    f_list = np.array([1, 1, 1, 1])
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)


def smooth_turn(rs: RobokitRS.RobokitRS, speed: int = 15):
    f_list = np.array([1, 1, 1, 1])
    s_list = np.array([speed, speed, speed, speed])
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
        s_list[1] = speed // 2
        f_list[3] = 0
    else:
        s_list[0] = speed // 2
        f_list[2] = 0
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)


def right(rs: RobokitRS.RobokitRS, speed: int = 15):
    f_list = np.array([0, 0, 1, 1])
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)

