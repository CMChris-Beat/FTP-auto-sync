import re
from datetime import datetime
from ftplib import FTP
from pathlib import Path
import pandas as pd
import os
import shutil


class ScanFiles:
    __SIZE_UNITS = list(f'{_}B'.strip() for _ in ' KMGTP')
    __EMPTY_DATA = pd.DataFrame()
    __PROJECT_DIR = os.path.dirname(os.path.dirname(Path(__file__).resolve()))
    __DATE_TODAY = datetime.today().strftime("%Y%m%d")

    def __init__(self, host: str, port: int, username: str, password: str,
                 FTP_DIR: str = None, BACKUP_DIR: str = None):
        """
        初始化FTP连接并登陆
        :param FTP_DIR: 必须填写为绝对路径
        :param BACKUP_DIR: 必须填写为绝对路径
        """
        self.FTP_DIR = (self.__PROJECT_DIR + "\\FTPData").replace('\\', '/') if FTP_DIR is None else FTP_DIR
        self.BACKUP_DIR = (self.__PROJECT_DIR + "\\BackupData").replace('\\', '/') if BACKUP_DIR is None else BACKUP_DIR
        self.f = FTP()
        print("正在尝试连接FTP服务器，请稍后...")
        self.f.connect(host=host, port=port)
        print("连接成功，正在登录...")
        self.f.login(user=username, passwd=password)
        print("已连接服务")
        self.local_data = pd.DataFrame(columns=['filename', 'size', 'is_dir'])
        self.ftp_data = pd.DataFrame(columns=['filename', 'size', 'is_dir'])

    @staticmethod
    def convert_size(size: int):
        """文件尺寸单位转换"""
        c = 0
        while size > 1024:
            size /= 1024
            c += 1
        return f"{size:.2f} {ScanFiles.__SIZE_UNITS[c]}"

    @staticmethod
    def analyze_ftp_line(line):
        """解析FTP文件系统信息行"""
        res = re.search(
            r'(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s(.*)',
            line)
        is_dir: bool = res.group(1).startswith('d')
        size: int = int(res.group(5))
        over_path: str = res.group(9)
        return {'is_dir': is_dir,
                'size': size,
                'item': over_path, }

    @staticmethod
    def default_callback(data: dict):
        """默认回调函数"""
        if data['is_dir']: return  # 开启此行不显示文件夹
        # print(f'{data["path"]} Sizes:{ScanFiles.convert_size(data["size"])}')

    @staticmethod
    def compare_datas(ftp_data: pd.DataFrame = __EMPTY_DATA,
                      local_data: pd.DataFrame = __EMPTY_DATA) -> dict:
        """
        对比FTP服务器与本地文件差异
        :param ftp_data: FTP服务器文件信息 pandas DataFrame格式
        :param local_data: 本地文件信息 pandas DataFrame格式
        :return (download, delete, modify): (下载、删除、修改) 本地需要的修改同步、删除或下载的文件列表 pandas DataFrame格式
        """
        ftp_data.loc[ftp_data['is_dir'] == "True", 'size'] = "0"
        inner_filename = pd.merge(ftp_data['filename'], local_data['filename'], how='inner').T.values[0]  # 求交集
        # intersected = pd.merge(ftp_data, local_data, how='inner')
        intersected = ftp_data.loc[[True if x in inner_filename else False for x in ftp_data['filename']]]
        download = pd.concat([ftp_data, intersected, intersected]).drop_duplicates(keep=False)  # 新文件下载

        intersected = local_data.loc[[True if x in inner_filename else False for x in local_data['filename']]]
        delete = pd.concat([local_data, intersected, intersected]).drop_duplicates(keep=False)  # 删除（需备份）

        modify = pd.DataFrame(columns=['filename', 'size', 'is_dir'])  # 被修改需下载（需备份）
        for file in inner_filename:  # FIXED: 被修改的文件无法识别（猜测交集数据不对，size不一样直接排除了）
            if ftp_data.loc[ftp_data['filename'] == file, 'size'].values[0] != local_data.loc[local_data['filename'] == file, 'size'].values[0]:
                modify.loc[modify.shape[0]] = ftp_data.loc[ftp_data['filename'] == file].values[0]
        # print(temp_modify)
        return {"download": download,
                "delete": delete,
                "modify": modify}

    def backup_files(self, delete_data: pd.DataFrame = __EMPTY_DATA, modify_data: pd.DataFrame = __EMPTY_DATA) -> None:
        """
        备份文件，将要被删除或修改的文件备份，以方便恢复
        :param delete_data: 对比文件树后传入的需要删除的文件列表 pd.DataFrame(columns=['filename', 'size', 'is_dir'])
        :param modify_data: 对比文件树后传入的需要修改的文件列表 pd.DataFrame(columns=['filename', 'size', 'is_dir'])
        """
        # FIXME: 没有需要再备份的文件也会建立文件夹树
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
        os.chdir(self.BACKUP_DIR)
        os.makedirs(self.__DATE_TODAY, exist_ok=True)  # 新建当天备份文件夹
        for file in delete_data.loc[delete_data['is_dir'].apply(lambda x: False if x == 'True' else True).values, 'filename']:
            backup = self.BACKUP_DIR + '/' + self.__DATE_TODAY + file[1:]
            print("删除备份中 " + backup)
            os.makedirs(os.path.dirname(backup), exist_ok=True)
            shutil.copy(self.FTP_DIR + file[1:], backup)
        for file in modify_data.loc[modify_data['is_dir'].apply(lambda x: False if x == 'True' else True).values, 'filename']:
            backup = self.BACKUP_DIR + '/' + self.__DATE_TODAY + file[1:]
            print("修改备份中 " + backup)
            os.makedirs(os.path.dirname(backup), exist_ok=True)
            shutil.copy(self.FTP_DIR + file[1:], backup)
            # os.makedirs(os.path.dirname(self.BACKUP_DIR + '/' + self.__DATE_TODAY + file[1:]), exist_ok=True)
            # shutil.copy(self.FTP_DIR + file[1:], self.BACKUP_DIR + '/' + self.__DATE_TODAY + file[1:])
        for di in delete_data.loc[delete_data['is_dir'].apply(lambda x: True if x == 'True' else False).values, 'filename']:
            os.makedirs(self.BACKUP_DIR + '/' + self.__DATE_TODAY + di[1:], exist_ok=True)
        for di in modify_data.loc[modify_data['is_dir'].apply(lambda x: True if x == 'True' else False).values, 'filename']:
            os.makedirs(self.BACKUP_DIR + '/' + self.__DATE_TODAY + di[1:], exist_ok=True)

    def download_file(self, download_data: pd.DataFrame = __EMPTY_DATA) -> None:  # DONE: 下载本地目录没有的FTP文件（无需备份）
        """
        建立文件夹并下载文件（必须执行local_walk后才可正常操作）
        :param download_data: 对比文件树后传入的需要下载的文件列表 pd.DataFrame(columns=['filename', 'size', 'is_dir'])
        """
        os.chdir(self.FTP_DIR)
        # 建立未有的文件夹
        for di in download_data.loc[download_data['is_dir'].apply(lambda x: True if x == 'True' else False).values, 'filename']:
            os.makedirs(di, exist_ok=True)
        # 下载文件
        for file in download_data.loc[download_data['is_dir'].apply(lambda x: False if x == 'True' else True).values, 'filename']:
            print("下载文件中 " + self.FTP_DIR + file[1:])
            try:
                with open(file, 'wb') as fi:
                    self.f.retrbinary('RETR ' + file, fi.write, 8*1024)
            finally:
                fi.close()

    def delete_file(self, delete_data: pd.DataFrame = __EMPTY_DATA) -> None:
        """
        删除本地文件
        :param delete_data: 对比文件树后传入的需要删除的文件列表 pd.DataFrame(columns=['filename', 'size', 'is_dir'])
        """
        for file in delete_data.loc[delete_data['is_dir'].apply(lambda x: False if x == 'True' else True).values, 'filename']:
            os.remove(self.FTP_DIR + file[1:])
        for di in delete_data.loc[delete_data['is_dir'].apply(lambda x: True if x == 'True' else False).values, 'filename']:
            os.rmdir(self.FTP_DIR + di[1:])

    def modify_file(self, modify_data: pd.DataFrame = __EMPTY_DATA) -> None:
        """
        下载并修改文件
        :param modify_data: 对比文件树后传入的需要修改的文件列表 pd.DataFrame(columns=['filename', 'size', 'is_dir'])
        """
        for file in modify_data.loc[modify_data['is_dir'].apply(lambda x: False if x == 'True' else True).values, 'filename']:
            print("修改文件中 " + self.FTP_DIR + file[1:])
            try:
                with open(self.FTP_DIR + file[1:], 'wb') as fi:
                    self.f.retrbinary('RETR ' + file, fi.write, 8*1024)
            finally:
                fi.close()

    def ftp_walk(self, p, callback=None):
        """
        遍历FTP服务器文件
        :param p: 起始路径
        :param callback: 回调函数, 传入类型为dict(keys: is_dir, size, item, path)
        :return:
        """
        if callback is None:
            callback = ScanFiles.default_callback
        lis = list()
        self.f.dir(p, lis.append)
        for line in lis:
            al = ScanFiles.analyze_ftp_line(line)
            al['path'] = f'{p}/{al["item"]}'.replace('\\', '/').replace('//', '/')
            callback(al)
            self.ftp_data.loc[self.ftp_data.shape[0]] = [al['path'], str(al['size']), str(al['is_dir'])]
            if al['is_dir']:
                self.ftp_walk(al['path'], callback)

    def local_walk(self, p, callback=None):
        """
        遍历本地文件
        :param p: 起始路径
        :param callback: 回调函数, 传入类型为dict(keys: is_dir, size, item, path)
        :return:
        """
        if callback is None:
            callback = ScanFiles.default_callback
        os.makedirs(self.FTP_DIR, exist_ok=True)
        os.chdir(self.FTP_DIR)
        for root, dirs, files in os.walk(p, topdown=False):
            for name in files:
                al = {
                    'is_dir': False,
                    'size': os.path.getsize(os.path.join(root, name)),
                    'item': os.path.join(root, name),
                    'path': os.path.join(root, name).replace('\\', '/')}
                callback(al)
                self.local_data.loc[self.local_data.shape[0]] = [al['path'], str(al['size']), str(al['is_dir'])]
            for name in dirs:
                al = {
                    'is_dir': True,
                    'size': os.path.getsize(os.path.join(root, name)),
                    'item': os.path.join(root, name),
                    'path': os.path.join(root, name).replace('\\', '/')}
                callback(al)
                self.local_data.loc[self.local_data.shape[0]] = [al['path'], str(al['size']), str(al['is_dir'])]

    def quit(self):
        """与FTP服务器断开连接"""
        self.f.quit()
