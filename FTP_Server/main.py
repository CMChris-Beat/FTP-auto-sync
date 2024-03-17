from FTPTools.process import Process
from FTPTools.process import timing
from threading import Thread


if __name__ == '__main__':
    process = Process(
        # host='192.168.19.130',  # 家里虚机
        host='192.168.244.128',  # 公司虚机
        port=21,
        username='ftp',
        password='123456',
        # FTP_DIR = "",  # 本地FTP备份路径
        # BACKUP_DIR = "",  # 本地删除或修改文件留存路径
    )
    Thread(target=timing, args=("13:20", 60, process.sync, True)).start()  # 定时同步
    # timing("11:29", 60, process.sync, True)  # 定时同步
    # timing("10:00", 86400, process.backup_deletion, False)  # 定时删除备份文件
