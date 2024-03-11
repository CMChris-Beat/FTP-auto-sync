from FTPTools import core
import time


class Process:
    def __init__(self, host: str, port: int, username: str, password: str, FTP_DIR: str = None, BACKUP_DIR: str = None):
        """
        :param host: 主机ip地址
        :param port: 主机FTP服务端口号
        :param username: 用户名
        :param password: 密码
        :param FTP_DIR: 本地FTP备份文件夹地址（绝对）
        :param BACKUP_DIR: 本地修改或删除文件再备份文件夹地址（绝对）
        """
        self.host = host
        self.port = port
        self.username = username
        self.passwd = password
        self.FTP_DIR = FTP_DIR
        self.BACKUP_DIR = BACKUP_DIR

    def sync(self) -> None:
        """
        Sync FTP Server Files
        """
        sf = core.ScanFiles(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.passwd,
            FTP_DIR=self.FTP_DIR,
            BACKUP_DIR=self.BACKUP_DIR,
        )
        try:
            print("同步开始", time.strftime("%H:%M:%S", time.localtime()))
            sf.ftp_walk('./')
            sf.local_walk('./')
            datas = sf.compare_datas(sf.ftp_data, sf.local_data)
            sf.download_file(datas['download'])
            sf.backup_files(datas['delete'], datas['modify'])
            sf.delete_file(datas['delete'])
            sf.modify_file(datas['modify'])
        finally:
            sf.quit()
            print("\n同步结束", time.strftime("%H:%M:%S", time.localtime()))

    def backup_deletion(self):
        # TODO: 定期删除备份文件夹
        pass


def timing(ti: str = "00:00", Interval_time: int = 60, func=None, heart: bool = True) -> None:
    """
    定时功能
    :param ti: 每天定时执行的时间 str[default: "00:00"]
    :param Interval_time: 轮询间隔时间，单位秒[s] int[default: 60]
    :param func: 需要定时执行的函数
    :param heart: 是否需要心跳显示 bool[default: True]
    :return: None
    """

    def heartbeat() -> None:
        print("Heartbeat ", time.strftime("%Y-%m-%d %H:%M", time.localtime()))

    if func is None:  # 没有传入函数时
        func = lambda: print("卖个萌awa")

    while True:
        if time.strftime("%H:%M", time.localtime()) == ti:
            func()
        if heart: heartbeat()
        time.sleep(Interval_time)
