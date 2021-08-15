import sys
import threading
from pynput import keyboard, mouse
import time
import json

# ---------------- <editor-fold desc="settings"> ----------------
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

output_info_listener = lambda s: None
action_listener = lambda key: None
state_listener = lambda s: None

# --- </editor-fold> ---


# ---------------- <editor-fold desc="private var"> ----------------
_play_thread = None
'''播放线程'''
_pause_flag = False
''' 在play循环时判断是否要挂起play子线程 '''
_stop_flag = False
''' 在play循环时判断是否要终止play子线程 '''
_hot_key_tmp_list = []
''' 按下热键时将临时放在这里，当有press发生时会与设置的热键或热键组合一一比对 '''
_output_info_list = []
''' 用于输出提示的按键记录 '''
_global_interval = 0.05
''' 公共CD, 每一条记录执行后执行sleep的时长'''
_crl = keyboard.Controller()
''' 按键控制器 '''


# --- </editor-fold> ---


# ---------------- <editor-fold desc="interface"> ----------------
def add_actions(actions):
    for a in actions:
        recode_list.append(a)


def open_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        global loop_count, start_play_key, pause_play_key, stop_play_key
        data = json.load(file)
        loop_count = int(data['loop_count'])
        start_play_key = data['start_play_key']
        pause_play_key = data['pause_play_key']
        stop_play_key = data['stop_play_key']
        recode_list.clear()
        for a in data['actions']:
            recode_list.append(a)
        output_info_listener('动作导入成功')


def save_file(path):
    if path:
        with open(path + '.json', 'w', encoding='utf-8') as file:
            res = {
                'loop_count': loop_count,
                'start_play_key': start_play_key,
                'pause_play_key': pause_play_key,
                'stop_play_key': stop_play_key,
                'actions': recode_list
            }
            file.write(json.dumps(res))
            output_info_listener('保存成功')


def set_loop_count(count: int):
    try:
        tmp = int(count)
        if not tmp == 0:
            global loop_count
            loop_count = tmp
            output_info_listener('设置成功')
    except ValueError:
        output_info_listener('设置失败')


def play(need_wait=False):
    global _play_thread, _stop_flag
    if _play_thread and _play_thread.is_alive():
        output_info_listener('正在播放动作')
    else:
        _play_thread = threading.Thread(target=__play_thread)
        _play_thread.setDaemon(True)
        _stop_flag = False
        _play_thread.start()
        output_info_listener('开始播放动作')
        if need_wait:
            _play_thread.join()


def pause_resume():
    global _pause_flag
    _pause_flag = 1 - _pause_flag
    output_info_listener('播放动作已暂停')


def stop():
    global _stop_flag
    _stop_flag = True
    output_info_listener('播放动作已终止')


def start_observer():
    # 启动键盘监听，热键+记录输入
    keyboard.Listener(on_press=lambda key: __global_keyboard_listener(__format_key(key, 'press')),
                      on_release=lambda key: __global_keyboard_listener(__format_key(key, 'release'))).start()
    # mouse.Listener(on_move=lambda x, y: None,
    #                on_click=lambda x, y, button, pressed: None,
    #                on_scroll=lambda x, y, x_axis, y_axis: None).start()


# --- </editor-fold> ---


# ---------------- <editor-fold desc="private methods"> ----------------
def __play_thread():
    time.sleep(2)
    count = loop_count
    while count:
        count -= 1
        for act in recode_list:
            if _global_interval:
                time.sleep(_global_interval)  # 公共CD
            key = keyboard.KeyCode.from_vk(act['vk'])
            if _stop_flag:
                output_info_listener('stopped')
                raise SystemError("手动强制结束！")
            elif _pause_flag:
                time.sleep(1)
                output_info_listener('paused')
            elif act['event'] == 'press':
                _crl.press(key)
                output_info_listener('press:%s' % act['name'])
            elif act['event'] == 'release':
                _crl.release(key)
            elif act['event'] == 'wait':
                time.sleep(act['vk'])


def __format_key(key, action):
    """
    键对象格式化成字典
    :param key: 键对象
    :return: 键字典
    """
    if isinstance(key, keyboard.Key):  # 控制键
        key = {
            'event': action,
            "name": key.name,
            "vk": key.value.vk
        }
    elif isinstance(key, keyboard._darwin.KeyCode):  # 字符建
        key = {
            'event': action,
            "name": str(key),
            "vk": key.vk
        }
    else:
        pass
    return key


def __global_keyboard_listener(key):
    # 输出按键信息
    if key['event'] == 'press':
        _output_info_list.append(key)
        tt = ''
        for k in _output_info_list:
            tt += '+' + k['name'] + '(vk:%s)' % k['vk']
        output_info_listener(tt[1::])
    else:
        _output_info_list.clear()
    # 调用callbacks
    action_listener(key)


def __global_mouse_listener(key, action):
    pass


# --- </editor-fold> ---

# --------------<editor-fold desc="main: 以脚本方式运行">--------------
if __name__ == '__main__':
    open_file('actions.action')
    loop_count = 10
    output_info_listener = lambda s: print(s)
    state_listener = lambda s: sys.exit(0) if s == 'stopped' else print(s)
    play(need_wait=True)
    print('完成并退出脚本')
# </editor-fold>

# --------------<editor-fold desc="动作文件示例及键位对照表">--------------

'''
{
    loop_count: 4,          # 循环次数，负数为无限循环
    start_play_key: [44],   # 设置热键
    actions:[
        {action: press, vk:5, name: 'g'},           # g键按下
        {action: release, vk:5, name: 'g'},         # g键抬起
        {action: wait, vk:2.5, name: second},       # 等待2.5秒
        {action: move, vk:-1, name: 'none', location: {x: 33, y:56}}, # 鼠标移动到屏幕坐标（33，56）位置
        {action: m_down, vk:312, name: 'm_left'},   # 鼠标左键按下
        {action: m_up, vk:312, name: 'm_left'},     # 鼠标左键抬起
        {action: m_scroll, vk:311, name: 'm_middle', location: {x: 0, y:-2}}, # 鼠标中键滚动
    ]
}

'''

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
# </editor-fold>
