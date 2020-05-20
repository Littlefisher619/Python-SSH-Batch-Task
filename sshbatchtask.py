# -*- coding: utf-8 -*-
import paramiko, os
from multiprocessing import Pool
import threading
import time, signal, traceback

key_file = ''
key_file_pwd = ''
progress = 0
length = 0
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1080)
# socket.socket = socks.socksocket

def initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def deploy_callback(result):
    global progress, length
    progress += 1
    print("(%d/%d) %s finished: %s" % (progress, length, result[0], result[1]))


def deploy(ip):
    try:
        global key_file, key_file_pwd
        privatekey = os.path.expanduser(key_file)  # 私钥文件

        key = paramiko.RSAKey.from_private_key_file(privatekey, key_file_pwd)

        ssh = paramiko.SSHClient()
        # ssh.load_system_host_keys(filename='/root/.ssh/known_hosts')
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, username='root', pkey=key)
        stdin, stdout, stderr = ssh.exec_command("""
            ls
        """)
        # print(str(stdout.read(),encoding='utf-8'),str(stderr.read(),encoding='utf-8'))

        errmsg = str(stderr.read(), encoding='utf-8')
        ssh.close()

        if errmsg != '':
            return ip, errmsg
        else:
            return ip, 'done!'

    except Exception as e:
        return ip, 'Error! \n%s' % traceback.format_exc()


def start():

    pool = Pool(processes=16)  # ,initializer=initializer)
    global length, progress
    target = open('target.txt', 'r').read().split('\n')
    #print(target)
    length = len(target)

    for x in range(0, length):
        print('(%d/%d) %s starting to execute commands...' % (x + 1, length, target[x]))
        pool.apply_async(func=deploy, args=(target[x],), callback=deploy_callback)
    # deploy(target[0])

    pool.close()
    print("Init...")
    pool.join()
    pool.terminate()


if __name__ == '__main__':
    start()
