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
from win32gui import FindWindow, GetWindowRect, SetForegroundWindow
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

    def logging(self, content):
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
window_rect = [each for each in GetWindowRect(hwnd)]

dicts = {
    'start': pickle.load(open('dicts/start.pkl', 'rb')),
    'plane': pickle.load(open('dicts/plane.pkl', 'rb')),
    'reconnect': pickle.load(open('dicts/reconnect.pkl', 'rb')),
    'cancel': pickle.load(open('dicts/cancel.pkl', 'rb')),
    'exit_to_lobby': pickle.load(open('dicts/exit_to_lobby.pkl', 'rb'))
}

start_rect = make_relative_rect(window_rect, [50, 680, -1100, -30])
mp_plane_rect = make_relative_rect(window_rect, [214, 600, -1070, -70])
plane_rect = make_relative_rect(window_rect, [76, 600, -1208, -70])
reconnect_rect = make_relative_rect(window_rect, [609, 447, -610, -299])
cancel_rect = make_relative_rect(window_rect, [670, 441, -589, -308])
exit_to_lobby_rect = make_relative_rect(window_rect, [1095, 660, -88, -83])

pwa_app = Pwa_app().connect(handle=hwnd)
window = pwa_app.window_()
actions = Actions(window)
while 1:
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

    if image_compare(dicts['reconnect'], ImageGrab.grab(reconnect_rect)) > 0.9:
        verboseprint('reconnect')
        actions.reconnect()
        continue

    if image_compare(dicts['cancel'], ImageGrab.grab(cancel_rect), 'L', 100) > 0.8:
        verboseprint('cancel')
        actions.cancel()
        continue
