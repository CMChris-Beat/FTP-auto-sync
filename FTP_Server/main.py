from FTPTools.process import Process
from FTPTools.process import timing
from threading import Thread
from datetime import datetime, timedelta


if __name__ == '__main__':
    process = Process(
        # host='192.168.19.130',  # 家里虚机
        host='192.168.244.128',  # 公司虚机
        port=21,
        username='ftp',
        password='123456',
        days=7  # 再备份文件留存天数
        # FTP_DIR = "",  # 本地FTP备份路径
        # BACKUP_DIR = "",  # 本地删除或修改文件留存路径
    )
    t = (datetime.today() + timedelta(minutes=1)).strftime("%H:%M")
    Thread(target=timing, args=(t, 60, process.sync, True)).start()  # 定时同步
