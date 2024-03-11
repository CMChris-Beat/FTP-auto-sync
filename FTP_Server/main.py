from FTPTools.process import sync


if __name__ == '__main__':
    sync(
        # host='192.168.19.130',  # 家里虚机
        host='192.168.244.128',  # 公司虚机
        port=21,
        username='ftp',
        password='123456',
        # FTP_DIR = "",  # 本地FTP备份路径
        # BACKUP_DIR = "",  # 本地删除或修改文件留存路径
    )

