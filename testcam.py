import urllib.request
import cv2, numpy as np
import asyncio

"""

HTTP/1.1 200 OK
Content-Type: multipart/x-mixed-replace;boundary=123456789000000000000987654321
Transfer-Encoding: chunked
Access-Control-Allow-Origin: *

GET /stream HTTP/1.1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5
Cache-Control: max-age=0
Connection: keep-alive
Host: 192.168.4.1:81
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36

"""


# 현재 카메라에 비치는 화면을 이미지로 가져오는 함수
async def get_robo_image(frame: np.ndarray):
    url = 'http://192.168.4.1:81/stream'
    s = urllib.request.urlopen(url)
    a_bytes = b''

    while True:
        try:
            # 64 바이트 씩 데이터 읽고 이미지 종료를 확인
            a_bytes += s.read(64)
            a = a_bytes.find(b'\xff\xd8')
            b = a_bytes.find(b'\xff\xd9')

            if a != -1 and b != -1:
                # 영상 한 장을 다 받으면 jpg로 인코딩 후 queue에 넣고 종료
                jpg = a_bytes[a:b + 2]
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                frame[:] = img
                # 처리된 이미지 이후의 데이터만 남기고 나머지는 제거
                a_bytes = a_bytes[b + 2:]
                await asyncio.sleep(0.01)
                
        except Exception as e:
            print("STREAM : ", e)
            continue


def get_load_region(image: np.ndarray, inrange_upper: tuple = (40, 255, 255), inrange_lower: tuple = (10, 40, 10), canny_threshold: tuple = (20, 30), kernel_size: tuple = (5, 5), dilate_iterations: int = 1, erode_iterations: int = 3):
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
    filled_image = np.zeros((h, w), np.uint8)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, inrange_lower, inrange_upper)
    
    canny = cv2.Canny(image, canny_threshold[0], canny_threshold[1])

    kernel = np.ones(kernel_size, np.uint8)
    dilated_canny = cv2.dilate(canny, kernel, iterations=dilate_iterations)
    eroded_mask = cv2.erode(mask, kernel, iterations=erode_iterations)
    # eroded_mask = mask

    y_idx, x_idx = np.where(eroded_mask == 255)

    if len(y_idx) == 0:
        return filled_image
    
    random_index = np.random.randint(0, len(y_idx))
    seed_point = (x_idx[random_index], y_idx[random_index])

    ff_mask = np.zeros((h + 2, w + 2), np.uint8)
    ff_mask[1:h+1, 1:w+1] = dilated_canny

    cv2.floodFill(filled_image, ff_mask, seed_point, 255, 0, 0, cv2.FLOODFILL_FIXED_RANGE)

    return filled_image


async def main():
    q = asyncio.Queue()
    # 카메라 스트림을 백그라운드에서 실행
    camera_task = asyncio.create_task(get_robo_image(q))
    
    print("start")
    while True:
        print("get")
        img = await q.get()
        cv2.imshow("test", img)
        cv2.imshow("load", get_load_region(img))
        
        if cv2.waitKey(1) == 27:
            break
    
    camera_task.cancel()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    asyncio.run(main())
