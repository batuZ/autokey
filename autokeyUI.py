import tkinter
from tkinter import ttk, filedialog, messagebox
import autokey
import sys

insert_key_list = []
insert_key_count = 0


def action_listener(key):
    if insert_key_focus_var.get():
        global insert_key_count
        after = insert_key_list[-1] if insert_key_list else None
        if key['event'] == 'press' and key != after:
            if insert_key_count == 0:
                insert_key_list.clear()
            insert_key_count += 1
            insert_key_list.append(key)
            key_to_str(insert_key_list)

        elif key['event'] == 'release':
            insert_key_count -= 1
            insert_key_list.append(key)
            key_to_str(insert_key_list)


def key_to_str(keys):
    res = fx = ''
    for key in keys:
        if key['event'] == 'press' or key['event'] == 'm_down':
            fx = '↓'
        elif key['event'] == 'release' or key['event'] == 'm_up':
            fx = '↑'
        res += "%s%s + " % (key['name'], fx)
    insert_key_var.set(res[:-2])


def insert_key_btn():
    autokey.add_actions(insert_key_list)
    [tv.delete(item) for item in tv.get_children()]
    [tv.insert('', 'end', values=(key["event"], key['vk'], key['name'])) for key in autokey.recode_list]
    clear_insert_list()


def clear_insert_list():
    insert_key_list.clear()
    insert_key_var.set('')


def insert_time_btn():
    if insert_time_var.get() > 0:
        autokey.add_actions([{'event': 'wait', 'vk': insert_time_var.get(), 'name': 'second'}])
        [tv.delete(item) for item in tv.get_children()]
        [tv.insert('', 'end', values=(key["event"], key['vk'], key['name'])) for key in autokey.recode_list]


def show_info(message):
    info_label["text"] = message


def open_file():
    path = filedialog.askopenfilename(filetypes=[('json', 'json')])
    if path:
        autokey.open_file(path)
        [tv.delete(item) for item in tv.get_children()]
        [tv.insert('', 'end', values=(key["event"], key['vk'], key['name'])) for key in autokey.recode_list]
        loop_num_var.set(autokey.loop_count)


if __name__ == '__main__':
    root = tkinter.Tk()
    root.title('Auto Key')
    root.resizable(0, 0)  # 固定尺寸
    root.geometry('+5+80')

    # ---------------- <editor-fold desc="菜单栏"> ----------------
    menuBar = tkinter.Menu(root)
    root.config(menu=menuBar)
    fileMenu = tkinter.Menu(menuBar)
    menuBar.add_cascade(label="File", menu=fileMenu)
    fileMenu.add_command(label="Open", command=open_file)
    fileMenu.add_command(label="Save", command=lambda: autokey.save_file(filedialog.asksaveasfilename()))
    fileMenu.add_command(label="Exit", command=lambda: sys.exit(0))
    # --- </editor-fold> ---

    # ----------------- <editor-fold desc="循环控制" defaultsect="collapsed"> ---------
    frame_loop_num = ttk.Frame(root)
    frame_loop_num.pack(fill=tkinter.X, padx=5, pady=5)
    tkinter.Label(frame_loop_num, text='循环次数(负数为无限循环):').grid()
    loop_num_var = tkinter.IntVar(value=1)
    loop_num_var.trace("w", lambda *s: autokey.set_loop_count(loop_num_var.get()))
    input_loop_num = ttk.Entry(frame_loop_num, textvariable=loop_num_var)
    input_loop_num.grid(row=0, column=1, sticky=tkinter.W + tkinter.E)
    frame_loop_num.columnconfigure(1, weight=1)
    # </editor-fold>

    # 方案列表
    tv = ttk.Treeview(root, show='headings', columns=('action', 'vk', 'name'), height=12)
    tv.column('action', width=10, anchor='w')
    tv.column('vk', width=10, anchor='w')
    tv.column('name', width=10, anchor='w')
    tv.heading('action', text='动作')
    tv.heading('vk', text='编号')
    tv.heading('name', text='按键')
    tv.pack(fill=tkinter.X)

    # ---------------- <editor-fold desc="记录按键"> ----------------
    frame_recode = tkinter.Frame(root)
    frame_recode.pack(padx=6, pady=6)

    ttk.Button(frame_recode, text='插入按键', command=insert_key_btn).grid(row=0, column=0)
    insert_key_var = tkinter.StringVar()
    insert_key_focus_var = tkinter.BooleanVar(value=False)
    # insert_key_label = ttk.Label(frame_recode, textvariable=insert_key_var)
    # insert_key_label.grid(row=0, column=1, sticky=tkinter.W)
    insert_key_entry = tkinter.Entry(frame_recode, textvariable=insert_key_var, state='readonly')
    insert_key_entry.grid(row=0, column=1, sticky=tkinter.W)
    insert_key_entry.bind('<FocusIn>', lambda event: insert_key_focus_var.set(True))
    insert_key_entry.bind('<FocusOut>', lambda event: insert_key_focus_var.set(False))

    ttk.Button(frame_recode, text='清空', command=clear_insert_list).grid(row=0, column=2)

    ttk.Button(frame_recode, text='插入时间', command=insert_time_btn).grid(row=1, column=0)
    insert_time_var = tkinter.DoubleVar()
    insert_time_entry = ttk.Entry(frame_recode, textvariable=insert_time_var)
    insert_time_entry.grid(row=1, column=1, sticky=tkinter.E + tkinter.W)
    insert_time_label = tkinter.Label(frame_recode, text='秒').grid(row=1, column=2, padx=5)
    # --- </editor-fold> ---

    # ---------------- <editor-fold desc="控制按钮"> ----------------
    frame_ctrl_btns = tkinter.Frame(root)
    frame_ctrl_btns.pack(pady=10)

    ttk.Button(frame_ctrl_btns, text='播放', command=lambda: autokey.play()).grid(row=0, column=0)
    ttk.Button(frame_ctrl_btns, text='暂停').grid(row=0, column=1)
    ttk.Button(frame_ctrl_btns, text='终止').grid(row=0, column=2)
    # --- </editor-fold> ---

    # 信息栏
    info_label = ttk.Label(root, text='')
    info_label.pack(fill=tkinter.X, side=tkinter.BOTTOM)
    autokey.output_info_listener = show_info  # 输出信息回调
    autokey.action_listener = action_listener
    autokey.start_observer()

    root.mainloop()

# TODO:
#       1、 hotkey test
#       2、 mouse recode & play
#       3、 script mode play
#       4、 write readme
