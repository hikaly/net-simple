# -*- coding: utf-8 -*-

import paramiko
import datetime


def pw_backup(remote_ip, login_user, login_pw, save_path, db_data_path, is_dir=False):
    flag_str = ''
    t = paramiko.Transport(remote_ip)
    save_name = db_data_path.split('/')[-1]
    # save_name = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + '.' + save_name.split('.')[1]
    try:
        t.connect(username=login_user, password=login_pw)  # 登录远程服务器
        sftp = paramiko.SFTPClient.from_transport(t)  # sftp传输协议
        local_path = '%s/%s' % (save_path, save_name)

        if is_dir:
            files = sftp.listdir(db_data_path)
        else:
            files = [db_data_path]

        for file_path in files:
            real_path = db_data_path+file_path
            print real_path, local_path
            sftp.get(real_path, local_path+file_path)

        flag_str = 'backup success'
    except Exception, e:
        flag_str = e.message
    finally:
        fp = open('./run.log', 'a+')
        w_str = '%s %s %s %s\n' % (datetime.datetime.now(), remote_ip, login_user, flag_str)
        fp.write(w_str)
        fp.close()
        t.close()


def file_upload(remote_ip, login_user, login_pw, file_path, save_path):
    flag_str = ''
    t = paramiko.Transport(remote_ip)
    try:
        t.connect(username=login_user, password=login_pw)  # 登录远程服务器
        sftp = paramiko.SFTPClient.from_transport(t)  # sftp传输协议
        print '----'
        sftp.put(file_path, save_path)
        flag_str = 'put success'
    except Exception, e:
        flag_str = e.message
    finally:
        print flag_str

if __name__ == '__main__':
    # 模拟服
    # pw_backup('106.75.93.166', 'ubuntu', '52Xiyou@jianke', 'db', '/home/ubuntu/login_info.txt')

    # 游戏工场-支付
    # pw_backup('114.215.134.133', 'root', 'Funship@ytjh', 'db', '/root/pay_server/netError/2017-06-29-16-19-23.html')

    # 游戏工场-登录
    # pw_backup('114.215.134.133', 'root', 'Funship@ytjh', 'db', '/root/NewLoginServer/netError/', True)

    # 游戏工场-游戏1
    # pw_backup('106.75.21.31', 'ubuntu', 'www.52xiyou.com', 'db', '/root/trunk/netError/', True)

    # 游戏工场-游戏2
    # pw_backup('121.42.24.116', 'root', 'Funship@ytjh', 'db/yxgc', '/root/trunk/netError/', True)

    # 腾讯云 登录服
    # pw_backup('118.89.61.50', 'ubuntu', 'www.52xiyou.com', 'db', '/home/ubuntu/login_server/netError/', True)

    # 游戏测试服
    # pw_backup('106.75.18.220', 'ubuntu', '52Xiyou@jianke', 'db/ceshi', '/data/trunk/netError/', True)

    # 测试登录服
    # pw_backup('106.75.18.220', 'ubuntu', '52Xiyou@jianke', 'db',  '/data/NewLoginServer/netError/', True)

    # 正式支付服
    # pw_backup('106.75.61.163', 'ubuntu', '52Xiyou@jianke', 'db', '/data/pay_server/netError/', True)

    # 测试支付服
    # pw_backup('106.75.61.163', 'ubuntu', '52Xiyou@jianke', 'db', '/data/project/pay_server/netError/', True)

    # 三国测试
    # pw_backup('106.75.25.205', 'ubuntu', '52Xiyou@jianke', 'db/sanguo', '/data/trunk/netError/', True)

    # 正式服
    pw_backup('106.75.61.165', 'ubuntu', '52Xiyou@jianke', 'db/linan', '/data/trunk/netError/', True)
    pass
