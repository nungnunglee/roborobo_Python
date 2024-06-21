from RobokitRS import *
from time import sleep
import keyboard
from moveFunc import *
from threading import Thread
import queue
from testcam import *
import cv2

# 로보 연결 및 작동 함수
def move_robo(action, *prams):

    # 영상을 받을 queue
    q = queue.Queue()

    # 로보 통신 객체 생성
    rs = RobokitRS.RobokitRS()

    # windows port number
    rs.port_open("COM5")

    # 초음파 센서 입력 버퍼 열기
    rs.sonar_begin(13)

    # 적외선 센서 입력 버퍼 열기 12: F, 2: B
    rs.set_pin_mode(12, RobokitRS.Modes.INPUT)
    rs.set_pin_mode(2, RobokitRS.Modes.INPUT)

    # 동기화를 위한 변수
    is_getting = False

    # 초기 영상
    frame = np.zeros((240, 320, 3), np.uint8)

    # 스레드 초기값
    thr = None

    # 영상 받고 행동하고 반복
    while True:

        # ESC 누를 때까지 반복
        if keyboard.is_pressed('ESC'):
            rs.end()
            break

        # 새로 받을 영상
        new_frame = None

        # 초음파 센서로 거리를 받기
        distance = rs.sonar_read(13)

        # 적외선 센서 읽기
        ir_f, ir_b = rs.digital_reads([12, 2])

        # 이전 행동에서 영상을 가져오는데 성공 했다면, 영상 가져오기 작업 시작
        if not is_getting:
            thr = Thread(target=get_robo_image, args=(q,))
            thr.start()
            is_getting = True

        # 스레드가 종료되었는지 0.5초 동안 확인
        thr.join(0.5)

        # 스래드가 아직 작업 중이면
        if thr.is_alive():
            print("can not get img")
            forward(rs, 0)
            continue
        else:
            # 작업이 끝났다면 영상 queue에서 꺼내기
            is_getting = False
            new_frame = q.get()

        # 새 영상을 가져왔다면 처리할 영상에 넣기
        if not is_getting:
            frame = new_frame

        # 마지막으로 읽은 영상 띄우기
        cv2.imshow("frame", frame)

        # 매개변수로 받은 영상 처리 및 행동 함수 실행
        action(rs, frame, (distance, ir_f, ir_b), prams)

        # 영상 출력 버퍼 및 모터 입력 버퍼 비울 시간 주기
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
