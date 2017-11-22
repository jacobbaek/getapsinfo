import paramiko
import time
import threading

g_list = []

def get_swinfo(target, user, passwd):
    paramiko.util.log_to_file("ssh_conn.log")
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try: 
        conn.connect(target, 22, user, passwd, timeout=5)
    except:
        return ""
    r_conn = conn.invoke_shell()

    r_conn.send("\n")
    r_conn.send("enable\n")
    r_conn.send(passwd + "\n")
    r_conn.send("show run | inc hostname\n")
    r_conn.send("show run | inc ip address 1.\n")
    r_conn.send("show inventory | inc SN\n")
    time.sleep(2)
    output = r_conn.recv(2000)
    return output

def load_list():
    with open('swlist.csv', 'r') as _file:
        swlist = _file.read()
    return swlist

def get_info(ipaddr):
    result = get_swinfo(ipaddr, "admin", "password")
    g_list.append(result)

def split_data(data):
    ip = ""
    serial = ""
    host = ""
    if data == None:
        g_list.append(None)
        return

    for item in data.split("\r"):
        if item.rfind("ip address") > 0:
            ip = item[13:-14]
        if item.rfind("SN:") > 0:
            serial = item[-12:]
        if item.rfind("hostname") > 0:
            host = item[9:]
    infos = [ip, serial, host]
    return infos

def main():
    global g_list
    threads = []
    iplist = load_list()
    for ip in iplist.split('\n'):
        t = threading.Thread(target=get_info, args=[ip.strip()])
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print "[info] request completed & extract infomations"

    with open('result.csv', 'w+') as _file:
        _file.write("ipaddr, serial_number, hostname\n")
        for l in g_list:
            data = split_data(l)
            if data == None:
                _file.write(",,,\n")
            else:
                _file.write(data[0] +", "+ data[1] +", "+ data[2] + "\n")

if __name__ == '__main__':
    main()