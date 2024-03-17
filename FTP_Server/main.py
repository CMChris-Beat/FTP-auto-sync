import json
from pprint import pprint
from FTPTools.process import Process
from FTPTools.process import timing
from threading import Thread
from datetime import datetime, timedelta


if __name__ == '__main__':
    config = json.load(open('./config.json', encoding='utf-8'))
    config['LOCAL_BACKUP_DIR'] = None if config['LOCAL_BACKUP_DIR'] == '' else config['LOCAL_BACKUP_DIR']
    config['RE_BACKUP_DIR'] = None if config['RE_BACKUP_DIR'] == '' else config['RE_BACKUP_DIR']
    config['FTP_SERVER_DIR'] = None if config['FTP_SERVER_DIR'] == '' else config['FTP_SERVER_DIR']

    process = Process(
        host=config['host'],
        port=config['port'],
        username=config['username'],
        password=config['password'],
        days=config['days'],  # 再备份文件留存天数
        FTP_DIR=config['LOCAL_BACKUP_DIR'],  # 本地FTP备份路径
        BACKUP_DIR=config['RE_BACKUP_DIR'],  # 本地删除或修改文件留存路径
        HOST_DIR=config['FTP_SERVER_DIR'],  # 远程目录地址
    )
    config['username'] = "*" * len(config['username'])
    config['password'] = "*" * len(config['password'])
    print("自动同步定时开始，如若没有问题，配置信息如下：")
    pprint(config, sort_dicts=False)
    t = (datetime.today() + timedelta(minutes=1)).strftime("%H:%M") if config['TestMode'] == "True" else config['Time']
    mode = "测试模式" if config['TestMode'] == "True" else "部署模式"
    print(f"\n目前在 {mode} 下, 定时同步时间为每日 {t}")

    sync = Thread(target=timing, args=(t, 60, process.sync, True)).start  # 定时同步
    backup_deletion = Thread(target=timing, args=(t, 60, process.backup_deletion, False)).start  # 定时删除再备份

    if config['sync'] == "True":
        sync()
    if config['backup_deletion'] == "True":
        backup_deletion()
