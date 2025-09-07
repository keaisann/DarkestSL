import ctypes
import base64
from gc import disable
import os

from icon import Icon
from tkinter import (
    BOTH,
    DISABLED,
    LEFT,
    NORMAL,
    NW,
    YES,
    BooleanVar,
    Button,
    Checkbutton,
    Entry,
    Frame,
    Tk,
    filedialog,
    messagebox,
)

from game_save_mgr import game


class Application(Frame):
    def __init__(self, *args: ..., **kwargs: ...):
        super().__init__(*args, **kwargs)
        self.pack()
        self.option_restart = BooleanVar()
        self.option_save = BooleanVar()
        self.file_name = Entry(state=DISABLED)
        self.create_widget()

    def create_widget(self):
        fm_top = Frame(self)
        Button(fm_top, text="保存", command=self.save_game, height=3, width=20).pack(
            side=LEFT, padx=5, pady=5
        )
        Button(fm_top, text="读取", command=self.restore_game, height=3, width=20).pack(
            side=LEFT, padx=5, pady=5
        )
        fm_top.pack(anchor=NW)

        fm_down = Frame(self)
        Checkbutton(
            fm_down, text="启动游戏", command=self.get_chk, variable=self.option_restart
        ).pack(side=LEFT)
        Checkbutton(
            fm_down,
            text="自定义存档名",
            command=self.get_chk,
            variable=self.option_save,
        ).pack(side=LEFT)
        fm_down.pack(anchor=NW, padx=5, pady=5, expand=YES, fill=BOTH)

    def get_chk(self):
        if self.option_save.get():
            self.file_name["state"] = NORMAL
            self.file_name.pack(padx=5, pady=5, expand=YES, fill=BOTH)
        else:
            self.file_name["state"] = DISABLED
            self.file_name.pack_forget()

    def save_game(self):
        exit_code, info = game.save_game(
            self.file_name.get() if self.option_save.get() else "", False
        )
        title = "操作成功"
        if exit_code:
            title = "操作失败"
        else:
            info = "文件已保存至%s" % game.backup_file
        messagebox.showinfo(title, info)

    def restore_game(self):
        backup_file = filedialog.askopenfilename(
            initialdir=game.backup_folder,
            title="Select file",
            filetypes=(("7zip files", "*.7z"), ("all files", "*.*")),
        )

        title = "操作成功"
        if backup_file != "":
            exit_code, info = game.game_restore(backup_file, self.option_restart.get())
            if not exit_code:
                title = "操作失败"
            if self.option_restart.get() == 0 or exit_code != 0:
                messagebox.showinfo(title, info)
            else:
                pass


root = Tk()
root.title("DarkestSL")
root.resizable(False, False)


with open("tmp.ico", "wb") as tmp:
    tmp.write(base64.b64decode(Icon().img))
root.iconbitmap("tmp.ico")  # type:ignore
os.remove("tmp.ico")

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
root.tk.call("tk", "scaling", ScaleFactor / 75)


app = Application(root)
app.mainloop()
