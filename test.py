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
    pass
