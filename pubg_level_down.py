import logging
import pickle
import Levenshtein
from time import sleep
from PIL import ImageGrab
from win32gui import FindWindow, GetWindowRect
from pywinauto import Application as Pwa_app
from pywinauto.keyboard import SendKeys


def image_compare(source_str, target_pic, mode='L'):
    target = target_pic.convert(mode)
    target_size = target.size
    target_img_arr = target.load()
    target_cur_str = ''
    if mode == 'L':
        for x in range(target_size[0]):
            for y in range(target_size[1]):
                if target_img_arr[x, y] < 192:
                    target_cur_str += '0'
                else:
                    target_cur_str += '1'

        return Levenshtein.ratio(source_str, target_cur_str)
    elif mode == 'RGB':
        for x in range(target_size[0]):
            for y in range(target_size[1]):
                # (R, G, B)
                if target_img_arr[x, y][2] < 50:
                    target_cur_str += '0'
                else:
                    target_cur_str += '1'

        return Levenshtein.ratio(source_str, target_cur_str)


class Actions:
    def __init__(self, window_obj):
        self.window = window_obj

    def start(self):
        # choose squad with double check
        self.window.ClickInput(coords=(100, 540))
        self.window.ClickInput(coords=(100, 540))

        # START
        self.window.ClickInput(coords=(100, 700))

    def quit(self):
        # esc
        SendKeys('{ESC}')
        # leave
        self.window.ClickInput(coords=(600, 440))
        # confirm
        self.window.ClickInput(coords=(570, 420))

    def reconnect(self):
        self.window.ClickInput(coords=(640, 430))


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

hwnd = FindWindow('UnrealWindow', None)
window_rect = [each for each in GetWindowRect(hwnd)]

start_rect = list(map(lambda x: x[0] + x[1], zip(window_rect, [50, 680, -1100, -30])))
plane_rect = list(map(lambda x: x[0] + x[1], zip(window_rect, [214, 600, -1070, -70])))
reconnect_rect = list(map(lambda x: x[0] + x[1], zip(window_rect, [590, 420, -590, -310])))

pwa_app = Pwa_app().connect(handle=hwnd)
window = pwa_app.window_()
actions = Actions(window)
while 1:
    sleep(5)
    if image_compare(pickle.load(open('dicts/start.pkl', 'rb')), ImageGrab.grab(start_rect)) > 0.98:
        logging.info('start')
        actions.start()
        continue

    if image_compare(pickle.load(open('dicts/plane.pkl', 'rb')), ImageGrab.grab(plane_rect), 'RGB') > 0.8:
        logging.info('quit')
        actions.quit()
        continue

    if image_compare(pickle.load(open('dicts/reconnect.pkl', 'rb')), ImageGrab.grab(reconnect_rect)) > 0.98:
        logging.info('reconnect')
        actions.reconnect()
        continue
