import sys
import threading
import tkinter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pynput import keyboard, mouse
import time
import json

# ---------------- <editor-fold desc="全局变量"> ----------------
play_thread = None
# 用于测试的按键记录
recode_list = []
# 在play循环时判断是否要挂起play子线程
pause_flag = False
# 在play循环时判断是否要终止play子线程
stop_flag = False

# 判断是否在录制状态，只有Ture时才会写记录
is_recoding = False
# 判断是否在play，避免重复play
is_playing = False

# 按下热键时将临时放在这里，当有press发生时会与设置的热键或热键组合一一比对
hot_key_tmp_list = []
start_play_key = [43]  # ,
pause_play_key = [47]  # .
stop_play_key = [44]  # /

output_info_list = []
crl = keyboard.Controller()


# --- </editor-fold> ---


def _global_keyboard_listener(key, action):
    """
    全局键盘监听
    :param key: 按键对象
    :param action: 动作
    :return: None
    """
    if is_recoding:
        # 记录按键
        key['event'] = action
        if key['name']:  # 处理一个vk为0的无名key
            recode_list.append(key)
            insert_key(key)
    else:
        # 进入热键控制，跳过记录
        _hot_key(key, action)

    # 输出按键信息
    if action == 'press':
        output_info_list.append(key)
        tt = ''
        for k in output_info_list:
            tt += '+' + k['name'] + '(vk:%s)' % k['vk']
        show_info(tt[1::])
    else:
        output_info_list.clear()


def _hot_key(key, action):
    """
    热键控制
    :param key: 键字典
    :param action: 动作
    :return: None
    """
    if action == 'press':
        # 有按键按下时，把vk塞进hot_key_tmp_list
        hot_key_tmp_list.append(key['vk'])
    elif action == 'release':
        # 有按键抬起时，判断hot_key_tmp_list里的值和哪个hotkey匹配
        if hot_key_tmp_list == start_play_key:
            play()
        elif hot_key_tmp_list == pause_play_key:
            global pause_flag
            pause_flag = 1 - pause_flag
        elif hot_key_tmp_list == stop_play_key:
            global stop_flag
            stop_flag = True
        else:
            pass
        # 清空hot_key_tmp_list
        hot_key_tmp_list.clear()
    else:
        pass


def play():
    """
    开始异步执行键盘动作
    :return: None
    """
    global play_thread, stop_flag
    if play_thread and play_thread.is_alive():
        print('playing...')
    else:
        play_thread = threading.Thread(target=_play_thread)
        play_thread.setDaemon(True)
        stop_flag = False
        play_thread.start()


def _play_thread(count=5):
    time.sleep(2)
    while count:
        count -= 1
        for act in recode_list:
            time.sleep(0.5)  # 公共CD
            key = keyboard.KeyCode.from_vk(act['vk'])
            if stop_flag:
                show_info('stopped')
                raise SystemError("手动强制结束！")
            elif pause_flag:
                time.sleep(1)
                show_info('paused')
            elif act['event'] == 'press':
                crl.press(key)
                show_info('press:%s' % act['name'])
            elif act['event'] == 'release':
                crl.release(key)
                show_info('playing ...')
            elif act['event'] == 'wait':
                time.sleep(act['vk'])


# ---------------- <editor-fold desc="工具函数"> ----------------
def format_key(key):
    """
    键对象格式化成字典
    :param key: 键对象
    :return: 键字典
    """
    if isinstance(key, keyboard.Key):  # 控制键
        key = {
            "name": key.name,
            "vk": key.value.vk
        }
    elif isinstance(key, keyboard._darwin.KeyCode):  # 字符建
        key = {
            "name": str(key),
            "vk": key.vk
        }
    else:
        pass
    return key


# --- </editor-fold> ---


# ---------------- <editor-fold desc="控件事件"> ----------------
def cb_change():
    """ check box change event """
    global is_recoding
    is_recoding = bool(1 - is_recoding)
    show_info('正在录制' if is_recoding else '停止录制')
    if is_recoding:
        input_time_btn['state'] = tkinter.NORMAL
        input_time_entry['state'] = tkinter.NORMAL
        show_info('正在录制')
    else:
        input_time_btn['state'] = tkinter.DISABLED
        input_time_entry['state'] = tkinter.DISABLED
        show_info('停止录制')


def show_info(message):
    """ 把message输出的信息栏"""
    info_label["text"] = message


def insert_key(key):
    key = format_key(key)
    recode_list.append(key)
    tv.insert('', 'end', values=(key["event"], key['vk'], key['name']))


def insert_wait():
    """ 插入时间间隔 """
    input_str = input_time_entry.get()
    try:
        num = float(input_str)
        _global_keyboard_listener({'name': 'second', 'vk': num}, 'wait')
        show_info('插入时间间隔%s秒' % input_str)
    except ValueError:
        show_info('输入错误，请输入整数或小数')


def show_dialog():
    tk.messagebox.showinfo(title='aa', message='cc')


def save_data():
    path = filedialog.asksaveasfilename()
    print(recode_list)
    if path:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(recode_list))
    else:
        print('cancel save')


# --- </editor-fold> ---


# ---------------- <editor-fold desc="__main__"> ----------------
if __name__ == '__main__':
    ''' UI '''
    root = tkinter.Tk()
    root.title('Auto Key')
    root.resizable(0, 0)  # 固定尺寸
    root.geometry('300x500+80+80')

    # 创建菜单栏功能
    menuBar = tkinter.Menu(root)
    root.config(menu=menuBar)

    # 菜单项
    fileMenu = tkinter.Menu(menuBar)
    menuBar.add_cascade(label="File", menu=fileMenu)
    fileMenu.add_command(label="Open", command=lambda: print(filedialog.askopenfilename()))
    fileMenu.add_command(label="Save", command=save_data)
    fileMenu.add_command(label="Exit", command=lambda: sys.exit(0))

    # 信息栏
    info_label = ttk.Label(root, text='')
    info_label.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    # 启动键盘监听，热键+记录输入
    keyboard.Listener(on_press=lambda key: _global_keyboard_listener(format_key(key), 'press'),
                      on_release=lambda key: _global_keyboard_listener(format_key(key), 'release')).start()

    # 方案列表
    tv = ttk.Treeview(root, show='headings', columns=('action', 'vk', 'name'))
    tv.column('action', width=100, anchor='w')
    tv.column('vk', width=100, anchor='w')
    tv.column('name', width=100, anchor='w')
    tv.heading('action', text='动作')
    tv.heading('vk', text='编号')
    tv.heading('name', text='按键')
    tv.pack()

    ttk.Checkbutton(root, text='录制', command=cb_change).pack()

    input_key_btn = ttk.Button(root, text="插入按键", state=tkinter.DISABLED, command=insert_key)
    input_key_btn.pack()
    input_time_btn = ttk.Button(root, text="插入时间间隔", state=tkinter.DISABLED, command=insert_wait)
    input_time_btn.pack()
    input_time_entry = tkinter.Entry(root, state=tkinter.DISABLED)
    input_time_entry.pack()

    ttk.Button(root, text="启动", command=play).pack()
    ttk.Button(root, text="暂停", command=None).pack()
    ttk.Button(root, text="终止", command=show_dialog).pack()

    root.mainloop()
# --- </editor-fold> ---
