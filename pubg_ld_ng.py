import win32gui
import win32ui
from ctypes import windll
from pywinauto import Application as Pwa_app
from pywinauto.keyboard import SendKeys
from pywinauto.controls import hwndwrapper
from PIL import Image, ImageGrab
from time import sleep
import win32con
import Levenshtein
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

hwnd = win32gui.FindWindow('UnrealWindow', None)

pwa_app = Pwa_app().connect(handle=hwnd)
res = hwndwrapper.HwndWrapper(hwnd)
print(res.send_keystrokes("{ESC}"))
# todo still has issue on clicking
exit()


def screenshot(handle):
    left, top, right, bot = win32gui.GetClientRect(handle)
    w = right - left
    h = bot - top
    hwndDC = win32gui.GetWindowDC(handle)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w - 200, h - 200)
    saveDC.SelectObject(saveBitMap)
    windll.user32.PrintWindow(handle, saveDC.GetSafeHdc(), 1)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(handle, hwndDC)

    return im


py_hwnd = win32ui.CreateWindowFromHandle(hwnd)

py_hwnd.SendMessage(win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, (510 << 16) | 100)
py_hwnd.SendMessage(win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, (510 << 16) | 100)

exit()

while 1:
    sleep(1)
    py_hwnd.SendMessage(win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, (510 << 16) | 100)
    py_hwnd.SendMessage(win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, (510 << 16) | 100)
    py_hwnd.PostMessage(win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
    py_hwnd.PostMessage(win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)
