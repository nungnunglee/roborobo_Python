import urllib.request
import cv2, numpy as np


# 현재 카메라에 비치는 화면을 이미지로 가져오는 함수
def get_robo_image(q):
    url = 'http://192.168.4.1:81/stream'
    s = urllib.request.urlopen(url)
    bytes = b''
    while True:
        try:
            bytes += s.read(64)
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = bytes[a:b + 2]
                # return cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
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
