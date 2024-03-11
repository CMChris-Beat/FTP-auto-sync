from FTPTools import core


def sync(host: str, port: int, username: str, password: str, FTP_DIR: str = None, BACKUP_DIR: str = None) -> None:
    """
    Sync FTP Server Files
    :param host: 主机ip地址
    :param port: 主机FTP服务端口号
    :param username: 用户名
    :param password: 密码
    :param FTP_DIR: 本地FTP备份文件夹地址（绝对）
    :param BACKUP_DIR: 本地修改或删除文件再备份文件夹地址（绝对）
    :return: None
    """
    sf = core.ScanFiles(
        host=host,
        port=port,
        username=username,
        password=password,
        FTP_DIR=FTP_DIR,
        BACKUP_DIR=BACKUP_DIR,
    )
    try:
        sf.ftp_walk('./')
        sf.local_walk('./')
        datas = sf.compare_datas(sf.ftp_data, sf.local_data)
        sf.download_file(datas['download'])
        sf.backup_files(datas['delete'], datas['modify'])
        sf.delete_file(datas['delete'])
        sf.modify_file(datas['modify'])
    finally:
        sf.quit()


def timing(time: str = "0:00:00") -> None:
    pass
