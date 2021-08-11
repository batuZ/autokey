import sys
import threading
from pynput import keyboard, mouse
import time
import json

# ---------------- <editor-fold desc="settings"> ----------------
action_path = 'actions.action'
''' 动作文件路径，用于打开或保存文件 '''
loop_count = 1
''' 循环次数，负数为无限循环 '''
recode_list = []
''' 动作集合 '''
start_play_key = [43]  # ,
''' 播放热键 '''
pause_play_key = [47]  # .
''' 暂停热键 '''
stop_play_key = [44]  # /
''' 终止热键 '''


# --- </editor-fold> ---


# ---------------- <editor-fold desc="interface"> ----------------
def open_file():
    pass


def save_file():
    path = filedialog.asksaveasfilename()
    print(recode_list)
    if path:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(recode_list))
    else:
        print('cancel save')


def play():
    pass


def pause():
    pass


def stop():
    pass


# --- </editor-fold> ---


# ---------------- <editor-fold desc="private var"> ----------------
_play_thread = None
'''播放线程'''
pause_flag = False
''' 在play循环时判断是否要挂起play子线程 '''
stop_flag = False
''' 在play循环时判断是否要终止play子线程 '''
is_recoding = False
''' 判断是否在录制状态，只有Ture时才会写记录 '''
is_playing = False
''' 判断是否在play，避免重复play '''
hot_key_tmp_list = []
''' 按下热键时将临时放在这里，当有press发生时会与设置的热键或热键组合一一比对 '''
output_info_list = []
''' 用于输出提示的按键记录 '''
crl = keyboard.Controller()
''' 按键控制器 '''
# --- </editor-fold> ---


''' vk  name
    0   a
    1   s
    2   d
    3   f
    4   h
    5   g
    6   z
    7   x
    8   c
    9   v
    11  b
    12  q
    13  w
    14  e
    15  r
    16  y
    17  t
    18  1
    19  2
    20  3
    21  4
    22  6
    23  5
    24  =
    25  9
    26  7
    27  -
    28  8
    29  0
    30  ]
    31  o
    32  u
    33  [
    34  i
    35  p
    36  enter
    37  l
    38  j
    39  '
    40  k
    41  ;
    42  \
    43  ,
    44  /
    45  n
    46  m
    47  .
    48  tab
    49  space
    50  `
    51  backspace
    53  esc
    54  command _r(右侧)
    55  command
    56  shift
    57  caps lock
    58  alt
    59  ctrl
    60  shift   _r
    61  alt     _r
    65  .       _s
    67  *       _s
    69  +       _s
    75  /       _s(小键盘)
    76  enter   _s
    78  -       _s
    82  0       _s
    83  1       _s
    84  2       _s
    85  3       _s
    86  4       _s
    87  5       _s
    88  6       _s
    89  7       _s
    91  8       _s
    92  9       _s
    96  F5
    97  F6
    98  F7
    99  F3
    100 F8
    101 F9
    103 F11
    109 F10
    111 F12
    115 home
    116 page_up
    118 F4
    119 end
    120 F2
    121 page_down
    122 F1
    123 left
    124 right
    125 down
    126 up

'''
