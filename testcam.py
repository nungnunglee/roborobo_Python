import urllib.request
import cv2, numpy as np


# 현재 카메라에 비치는 화면을 이미지로 가져오는 함수
def get_robo_image(q):

    # 카메라 스트림 소켓 url
    url = 'http://192.168.4.1:81/stream'

    # 스트림 열기
    s = urllib.request.urlopen(url)

    # 이진 코드 저장할 변수 선언
    bytes = b''

    # 영상 한 장 읽기
    while True:
        try:
            # 64 바이트 씩 데이터 읽고 이미지 종료를 확인
            bytes += s.read(64)
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')

            if a != -1 and b != -1:
                # 영상 한 장을 다 받으면 jpg로 인코딩 후 queue에 넣고 종료
                jpg = bytes[a:b + 2]
                q.put(cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR))
                return
            # 240, 320, 3
        except Exception as e:
            print("STREAM : ", e)
            continue


if __name__ == '__main__':
    while True:
        img = get_robo_image()
        cv2.imshow("test", img)

        # ESC키를 누를 때 까지 반복
        if cv2.waitKey(1) == 27:
            break
