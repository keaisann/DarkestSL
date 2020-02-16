import io
import os
import subprocess
import time
import webbrowser

from datetime import datetime
from configparser import ConfigParser, NoOptionError


def run_cmd(cmd):
    sub_p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
    sub_p.wait()
    stream_stdout = io.TextIOWrapper(sub_p.stdout).read()
    stream_stderr = io.TextIOWrapper(sub_p.stderr).read()
    exit_code = 0
    info = ''
    if stream_stdout != '':
        print(stream_stdout)
        info = stream_stdout
    if stream_stderr != '':
        print(stream_stderr)
        info = stream_stderr
        exit_code = 1
    return exit_code, info


class GameSaveMgr(object):
    def __init__(self, program_name, p7zip_path, save_folder, backup_folder, rungame_url):
        self.program_name = program_name
        self.rungame_url = rungame_url
        self.p7zip_path = p7zip_path
        self.save_folder = save_folder
        self.backup_folder = backup_folder
        self.backup_file = ''
        self.sleep_sec = 0

    def game_save(self, filename='', overwrite=1):
        """文件名默认为时间戳，若指定非空文件名则默认覆盖，不覆盖则文件名追加时间戳。
        参数:
            filename: 指定的文件名
            overwrite: 指定是否覆盖
        """

        timestamp = datetime.now().strftime('%Y-%m-%d_%H_%M_%S_%f')
        if filename == '':
            self.backup_file = os.path.join(self.backup_folder, timestamp)
        elif overwrite == 1:
            self.backup_file = os.path.join(self.backup_folder, filename)
        else:
            self.backup_file = os.path.join(self.backup_folder, filename + '_' + timestamp)

        zip_format = '7z'  # 注意：经测试，不支持gzip，bzip2。

        # 拼接并执行命令，删除同名文件后更新压缩包。
        cmd = '\"%s\" a -t%s \"%s\" \"%s\"' % (self.p7zip_path, zip_format, self.backup_file, self.save_folder)
        try:
            os.remove(self.backup_file + '.%s' % zip_format)
            print('将覆盖原文件')
        except FileNotFoundError:
            print('将创建新文件')
        finally:
            return run_cmd(cmd)

    def game_load(self, backup_file_path):
        """从备份目录指定文件，恢复至存档目录，并且静默覆盖"""
        restore_dir = os.path.join(self.save_folder, '..')
        cmd = "\"%s\" x \"%s\" -o\"%s\" -aoa" % (self.p7zip_path, backup_file_path, restore_dir)
        return run_cmd(cmd)

    def backup_list(self):
        """按创建时间倒序返回备份文件名列表"""
        file_list = os.listdir(self.backup_folder)
        backup_list = []
        for file in file_list:
            backup_list.append([file, os.path.getctime(self.backup_folder + '\\' + file)])
        backup_list = sorted(backup_list, key=lambda time: time[1], reverse=1)
        return backup_list

    def kill_game_process(self):
        """
        当进程不存在，或者被成功杀死时返回0(成功)，其它错误返回1(失败)
        返回值格式：(状态码, 状态信息)
        """
        # 当指定游戏进程不存在时，返回值为0。
        cmd = 'taskkill /F /IM %s' % self.program_name
        exit_code, info = run_cmd(cmd)
        if info == '错误: 没有找到进程 "%s"。\n' % self.program_name:
            exit_code = 0
        return exit_code, info

    def run_game(self):
        """启动游戏，此方法无法获取返回值"""
        webbrowser.open(self.rungame_url)

    def game_restore(self, backup_file, restart_game=False):
        exit_code, info = self.kill_game_process()
        if not exit_code:
            exit_code, info = self.game_load(backup_file)
        if (not exit_code) and restart_game:
            time.sleep(self.sleep_sec)
            self.run_game()
        return exit_code, info


cfg = ConfigParser()
cfg.read(os.path.join(os.getcwd(), 'config.ini'))

p_name = cfg.get('Game', 'program_name')
p7z_path = cfg.get('Game', 'p7zip_path')
sv_folder = cfg.get('Game', 'save_folder')
steam_rg_url = cfg.get('Game', 'steam_rungame_url')
bak_folder = cfg.get('Game', 'backup_folder')

game = GameSaveMgr(p_name, p7z_path,
                   sv_folder,
                   bak_folder,
                   steam_rg_url)

try:
    game.sleep_sec = int(cfg.get('Game', 'sleep_sec'))
except NoOptionError:
    pass

if __name__ == '__main__':
    pass
