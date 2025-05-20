from RobokitRS import *
from moveFunc import *
import asyncio
import cv2
import numpy as np
import logging
import urllib.request


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class Robo:
    def __init__(self, port_name: str = "COM5", max_speed: int = 15, run_mode: str = "line"):
        self.q = asyncio.Queue()
        self.rs = RobokitRS.RobokitRS()
        self.rs.port_open(port_name)
        # self.rs.sonar_begin(13)

        self.momentum = "left"
        self.max_speed = max_speed
        self.run_mode = run_mode
        self.frame = np.zeros((240, 320, 3), np.uint8)
        asyncio.create_task(get_robo_image(self.frame))
        logger.info("Robo 초기화 완료")

    async def move(self):
        while True:
            cv2.imshow("frame", self.frame)

            if self.run_mode == "line":
                await self.line_action()

            await asyncio.sleep(0.01)
            if cv2.waitKey(1) == 27:
                break
    
    async def line_action(self):
        
        load_region = get_load_region(self.frame)
        cv2.imshow("load", load_region)

        x_idx, _ = np.where(load_region == 255)

        if len(x_idx) == 0:
            logger.info(f"load_region is empty. momentum: {self.momentum}")
            if self.momentum == "left":
                turn(self.rs, self.max_speed)
            else:
                turn(self.rs, self.max_speed * -1)
            return

        padding = 20

        x_mean = x_idx.mean()

        turn_speed = (160 - x_mean) / 160 * self.max_speed

        logger.info(f"turn_speed: {turn_speed}\r")

        if np.abs(turn_speed) < padding:
            forward(self.rs, self.max_speed)
            return

        self.momentum = "right" if turn_speed > 0 else "left"
        smooth_turn(self.rs, turn_speed)


if __name__ == '__main__':
    robo = Robo()
    asyncio.run(robo.move())
