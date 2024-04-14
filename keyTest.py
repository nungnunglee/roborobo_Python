import keyboard


def keyboard_down(evt):
    # 입력된 키를 출력
    print('Keyboard down {} \n'.format(evt.name))


# 키보드 버튼을 누르면 keyboard_down 함수를 호출
keyboard.on_press(keyboard_down)

# esc 키를 누를때 까지 대기
keyboard.wait('esc')
