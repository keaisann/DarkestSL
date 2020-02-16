import base64
import os

from icon import Icon
from tkinter import *  # 注意模块导入方式，否则代码会有差别
from tkinter import filedialog
from tkinter import messagebox

from game_save_mgr import game


class Application(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        self.restart_option = BooleanVar()
        self.save_file_name_fmt = ''
        self.file_name_entry = Entry(state='disabled')
        self.save_option = BooleanVar()
        self.create_widget()

    def create_widget(self):
        fm_top = Frame(self)
        Button(fm_top, text='保存', command=self.save_game, height=2, width=20).pack(side=LEFT, padx=5, pady=5)
        Button(fm_top, text='读取', command=self.restore_game, height=2, width=20).pack(side=LEFT, padx=5, pady=5)
        fm_top.pack(anchor=NW)

        fm_down = Frame(self)
        Checkbutton(fm_down, text='启动游戏', command=self.get_chk, variable=self.restart_option).pack(side=LEFT)
        Checkbutton(fm_down, text='自定义存档名', command=self.get_chk, variable=self.save_option).pack(side=LEFT)
        fm_down.pack(anchor=NW, padx=5, pady=5, expand=YES, fill=BOTH)
        self.file_name_entry.pack(padx=5, pady=5, expand=YES, fill=BOTH)

    def get_chk(self):
        if self.save_option.get():
            self.file_name_entry['state'] = 'normal'
        else:
            self.file_name_entry.delete(0, END)
            self.file_name_entry['state'] = 'disabled'

    def save_game(self):
        exit_code, info = game.game_save(self.file_name_entry.get(), 0)
        title = '操作成功'
        if exit_code:
            title = '操作失败'
        else:
            info = '文件已保存至%s' % game.backup_file
        messagebox.showinfo(title, info)

    def restore_game(self):
        backup_file = filedialog.askopenfilename(initialdir=game.backup_folder, title="Select file",
                                                 filetypes=(("7zip files", "*.7z"), ("all files", "*.*")))
        print(backup_file)

        title = '操作成功'
        if backup_file != '':
            exit_code, info = game.game_restore(backup_file, self.restart_option.get())
            if not exit_code:
                title = '操作失败'
            if self.restart_option.get() == 0 or exit_code != 0:
                messagebox.showinfo(title, info)
            else:
                pass


root = Tk()
root.title('DarkestSL')
root.resizable(0, 0)

with open('tmp.ico', 'wb') as tmp:
    tmp.write(base64.b64decode(Icon().img))
root.iconbitmap('tmp.ico')
os.remove('tmp.ico')

app = Application(root)
app.mainloop()
