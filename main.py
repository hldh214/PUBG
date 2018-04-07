import argparse
import json
import logging
import pickle
import Levenshtein
import requests
from time import sleep, time
from PIL import ImageGrab
from pywinauto import Application as Pwa_app
from pywinauto.keyboard import SendKeys
from win32gui import ClientToScreen, FindWindow, GetClientRect, SetForegroundWindow
from random import randint
from pyautogui import keyDown, keyUp, press


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


def make_relative_rect(source, diff):
    return list(map(lambda x: x[0] + x[1], zip(source, diff)))


class Notify:
    def __init__(self, method):
        self.config = json.load(open('./config.json')).get('notify')
        self.method = getattr(self, method)

    @staticmethod
    def logging(content):
        logging.info(content)

    def ftqq(self, content):
        sckey = self.config['ftqq']['sckey']
        title = self.config['ftqq']['title']
        textmod = {'text': title, 'desp': content}
        requests.post('https://sc.ftqq.com/{0}.send'.format(sckey), textmod)


class Actions:
    team_coords = {
        'solo-squad': (100, 560),
        'squad': (100, 540),
        'duo': (100, 520),
        'solo': (100, 500)
    }

    def __init__(self, window_obj):
        self.window = window_obj

    def start(self, team):
        # choose TEAM with double check
        self.window.ClickInput(coords=self.team_coords[team])
        self.window.ClickInput(coords=self.team_coords[team])

        # START
        self.window.ClickInput(coords=(100, 700))

        # refresh lobby if necessary (#4)
        times = 0
        while times < 10:
            sleep(3)
            if image_compare(dicts['tl_pubg_logo'], ImageGrab.grab(tl_pubg_logo_rect), 'L', 70) > 0.9:
                times += 1
            else:
                return None

        self.quit()

    def autoplay(self):
        wait_for_plane = randint(15, 40)
        sleep(wait_for_plane)
        press('f')
        timeout = time() + 285 - wait_for_plane
        keyDown('w')
        keyDown('space')
        while True:
            sleep(5)
            if time() >= timeout:
                keyUp('w')
                keyUp('space')
                press('s')
                break
            elif image_compare(dicts['exit_to_lobby'], ImageGrab.grab(exit_to_lobby_rect)) > 0.8:
                self.quit()
                break

    def quit(self):
        # esc
        SendKeys('{ESC}')
        # leave
        self.window.ClickInput(coords=(600, 440))
        # confirm
        self.window.ClickInput(coords=(570, 420))

    def reconnect(self):
        self.window.ClickInput(coords=(640, 450))

    def cancel(self):
        self.window.ClickInput(coords=(670, 440))


parser = argparse.ArgumentParser()
parser.add_argument(
    '-t', '--team',
    help='choose the type of team',
    choices=('solo', 'duo', 'squad', 'solo-squad'),
    default='solo'
)
parser.add_argument(
    '-m', '--mode',
    help='operating mode',
    choices=('derank', 'bps'),
    default='bps'
)
parser.add_argument(
    '-n', '--notify',
    help='notify method',
    choices=('ftqq', 'logging'),
    default='logging'
)
parser.add_argument(
    '-v', '--verbose',
    help='verbose output',
    action='count',
    default=0
)
args = parser.parse_args()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
notify = Notify(args.notify)
verboseprint = notify.method if args.verbose else lambda *a, **k: None
round_count = 0

hwnd = FindWindow('UnrealWindow', None)
SetForegroundWindow(hwnd)
_left, _top, _right, _bottom = GetClientRect(hwnd)
left, top = ClientToScreen(hwnd, (_left, _top))
right, bottom = ClientToScreen(hwnd, (_right, _bottom))
window_rect = [left, top, right, bottom]
dicts = {
    'start': pickle.load(open('dicts/start.pkl', 'rb')),
    'plane': pickle.load(open('dicts/plane.pkl', 'rb')),
    'reconnect': pickle.load(open('dicts/reconnect.pkl', 'rb')),
    'cancel': pickle.load(open('dicts/cancel.pkl', 'rb')),
    'exit_to_lobby': pickle.load(open('dicts/exit_to_lobby.pkl', 'rb')),
    'tl_pubg_logo': pickle.load(open('dicts/tl_pubg_logo.pkl', 'rb')),
    'timeout': pickle.load(open('dicts/timeout.pkl', 'rb'))
}

start_rect = make_relative_rect(window_rect, [42, 649, -1092, -22])
mp_plane_rect = make_relative_rect(window_rect, [206, 569, -1062, -62])
plane_rect = make_relative_rect(window_rect, [68, 569, -1200, -62])
reconnect_rect = make_relative_rect(window_rect, [601, 399, -602, -309])
reconnect_ng_rect = make_relative_rect(window_rect, [601, 416, -602, -292])
timeout_rect = make_relative_rect(window_rect, [636, 407, -626, -295])
cancel_rect = make_relative_rect(window_rect, [662, 410, -581, -300])
exit_to_lobby_rect = make_relative_rect(window_rect, [1087, 629, -80, -75])
tl_pubg_logo_rect = make_relative_rect(window_rect, [50, 27, -1197, -676])

pwa_app = Pwa_app().connect(handle=hwnd)
window = pwa_app.window_()
actions = Actions(window)
while True:
    sleep(5)
    if image_compare(dicts['start'], ImageGrab.grab(start_rect)) > 0.98:
        verboseprint('start')
        round_count = round_count + 1
        if round_count % 10 == 0:
            notify.method('Starting the {0}th game'.format(round_count))
        actions.start(args.team)
        continue

    if image_compare(dicts['exit_to_lobby'], ImageGrab.grab(exit_to_lobby_rect)) > 0.8:
        verboseprint('quit')
        actions.quit()
        continue

    if image_compare(dicts['plane'], ImageGrab.grab(plane_rect), 'RGB') > 0.7 \
            or image_compare(dicts['plane'], ImageGrab.grab(mp_plane_rect), 'RGB') > 0.8:
        if args.mode == 'bps':
            actions.autoplay()
        verboseprint('quit')
        actions.quit()
        continue

    if image_compare(dicts['reconnect'], ImageGrab.grab(reconnect_rect)) > 0.8 \
            or image_compare(dicts['reconnect'], ImageGrab.grab(reconnect_ng_rect)) > 0.8 \
            or image_compare(dicts['timeout'], ImageGrab.grab(timeout_rect)) > 0.8:
        verboseprint('reconnect')
        actions.reconnect()
        continue

    if image_compare(dicts['cancel'], ImageGrab.grab(cancel_rect), 'L', 100) > 0.8:
        verboseprint('cancel')
        actions.cancel()
        continue
