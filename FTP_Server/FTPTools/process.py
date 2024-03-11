from FTPTools import core


def sync(host: str, port: int, username: str, password: str, FTP_DIR: str = None, BACKUP_DIR: str = None) -> None:
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
