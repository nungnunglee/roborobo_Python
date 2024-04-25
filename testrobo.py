from RobokitRS import *
from time import sleep
import keyboard
from moveFunc import *

rs = RobokitRS.RobokitRS()

# windows port number
rs.port_open("COM5")

# linux port number
# rs.port_open("/dev/ttyUSB0")

# 초음파 센서 입력 버퍼 열기
rs.sonar_begin(2)

# 적외선 센서 입력 버퍼 열기 12: R, 13: L
rs.set_pin_mode(12, RobokitRS.Modes.INPUT)
rs.set_pin_mode(13, RobokitRS.Modes.INPUT)

# 검은 선 따라가기
def line_track(speed=10):
    while True:
        # ESC 누를 때 까지 무한 반복
        if keyboard.is_pressed('ESC'):
            rs.end()
            break

        # 초음파 센서로 거리를 받기
        distance = rs.sonar_read(2)

        # 12, 13번 핀(적외선 센서)에서 True 또는 False 받기
        digital_list = rs.digital_reads(list(range(12, 14)))

        # 거리가 30cm 이상일 경우
        if distance >= 30:

            if digital_list[0]:
                if digital_list[1]:
                    # 둘 다 감지 할 경우
                    forward(rs, speed)
                else:
                    # 오른쪽(12번)만 감지할 경우
                    turn(rs, -10)
            else:
                if digital_list[1]:
                    # 왼쪽(13번)만 감지할 경우
                    turn(rs, speed)
                else:
                    # 둘 다 감지 못 할 경우
                    forward(rs, 0)

            # 로봇이 버퍼 비울 시간 동안 대기
            sleep(0.1)

        elif distance < 30:
            # 거리가 30cm 미만 일 경우 정지
            forward(rs, 0)
            sleep(0.1)


def key_control():
    while True:
        # ESC 누를 때 까지 무한 반복
        if keyboard.is_pressed('ESC'):
            rs.end()
            break

        # 전진 우회전 속도 0으로 초기화
        f_speed, r_speed = 0, 0

        # 각 방향 화살표 키 입력 시
        if keyboard.is_pressed("left"):
            r_speed = -15
        elif keyboard.is_pressed("right"):
            r_speed = 15
        elif keyboard.is_pressed("up"):
            f_speed = 15
        elif keyboard.is_pressed("down"):
            f_speed = -15

        # 초음파 센서로 거리를 받기
        distance = rs.sonar_read(2)

        # 12, 13번 핀(적외선 센서)에서 True 또는 False 받기
        digital_list = rs.digital_reads(list(range(12, 14)))

        # 우회전 속도가 0 이 아니면 그 속도로 우회전
        if r_speed != 0:
            turn(rs, r_speed)

        # 적외선 센서로 감지가 되거나(앞에 땅이 있거나) 후진일 경우 기동
        elif (digital_list[0] or digital_list[1]) or (f_speed < 0):
            forward(rs, f_speed)

        # 로봇이 버퍼 비울 시간 동안 대기
        sleep(0.1)


if __name__ == '__main__':
    key_control()
    # line_track(15)
