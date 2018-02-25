import logging
import pickle
import Levenshtein
from time import sleep
from PIL import ImageGrab
from win32gui import FindWindow, GetWindowRect
from pywinauto import Application as Pwa_app
from pywinauto.keyboard import SendKeys


def image_compare(source_str, target_pic, mode='L', threshold=192):
    target = target_pic.convert(mode)
    target_size = target.size
    target_img_arr = target.load()
    target_cur_str = ''
    if mode == 'L':
        for x in range(target_size[0]):
            for y in range(target_size[1]):
                # todo: rework
                if target_img_arr[x, y] < threshold:
                    target_cur_str += '0'
                else:
                    target_cur_str += '1'

        return Levenshtein.ratio(source_str, target_cur_str)
    elif mode == 'RGB':
        for x in range(target_size[0]):
            for y in range(target_size[1]):
                # (R, G, B) yellow region
                if target_img_arr[x, y][2] < 50 \
                        and target_img_arr[x, y][1] > 200 \
                        and target_img_arr[x, y][0] > 200:
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
        # loading issue
        sleep(5)
        self.window.ClickInput(coords=(640, 430))

    def cancel(self):
        self.window.ClickInput(coords=(670, 440))


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

hwnd = FindWindow('UnrealWindow', None)
window_rect = [each for each in GetWindowRect(hwnd)]

dicts = {
    'start': pickle.load(open('dicts/start.pkl', 'rb')),
    'plane': pickle.load(open('dicts/plane.pkl', 'rb')),
    'reconnect': pickle.load(open('dicts/reconnect.pkl', 'rb')),
    'cancel': pickle.load(open('dicts/cancel.pkl', 'rb'))
}

start_rect = list(map(lambda x: x[0] + x[1], zip(window_rect, [50, 680, -1100, -30])))
mp_plane_rect = list(map(lambda x: x[0] + x[1], zip(window_rect, [214, 600, -1070, -70])))
plane_rect = list(map(lambda x: x[0] + x[1], zip(window_rect, [76, 600, -1208, -70])))
reconnect_rect = list(map(lambda x: x[0] + x[1], zip(window_rect, [590, 420, -590, -310])))
cancel_rect = list(map(lambda x: x[0] + x[1], zip(window_rect, [670, 441, -589, -308])))

pwa_app = Pwa_app().connect(handle=hwnd)
window = pwa_app.window_()
actions = Actions(window)
while 1:
    sleep(5)
    if image_compare(dicts['start'], ImageGrab.grab(start_rect)) > 0.98:
        logging.info('start')
        actions.start()
        continue

    if image_compare(dicts['plane'], ImageGrab.grab(plane_rect), 'RGB') > 0.7 \
            or image_compare(dicts['plane'], ImageGrab.grab(mp_plane_rect), 'RGB') > 0.8:
        logging.info('quit')
        actions.quit()
        continue

    if image_compare(dicts['reconnect'], ImageGrab.grab(reconnect_rect)) > 0.98:
        logging.info('reconnect')
        actions.reconnect()
        continue

    if image_compare(dicts['cancel'], ImageGrab.grab(cancel_rect), 'L', 100) > 0.8:
        logging.info('cancel')
        actions.cancel()
        continue
