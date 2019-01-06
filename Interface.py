import binascii

import serial

import os

import time

interface_name = ''


def interface_swicth(b, name):
    global interface_name
    interface_name = name

    try:
        ser = serial.Serial(interface_name, 115200, timeout=0.5)  # winsows系统使用com8口连接串行口
        if b:
            if not ser.is_open:
                ser.open()
        else:
            if ser.is_open:
                ser.close()
        return True
    except Exception as e:
        print('错误')
        print(e)
        return False


def get_data_from_interface():
    print('启动数据')
    ser = serial.Serial(interface_name, 115200, timeout=0.5)  # winsows系统使用com8口连接串行口
    if not ser.is_open:
        ser.open()  # 打开端口

    # f = open('./data.txt', 'w+')

    if not os.path.exists('./数据'):
        os.makedirs('./数据')

    filename = 'datasource_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    f = None
    print('打开文件')
    while True:
        line_str = ser.readline()
        if len(line_str) != 37:
            print('数据长度不够')
            if f is not None:
                f.close()
            continue
        str = binascii.b2a_hex(line_str).decode('utf8')
        print(str)
        if f is None or f.closed:
            f = open('./数据/%s.txt' % filename, 'a')
        f.write(str + '\n')
        LD = word_num(str[0:4], str[18:22])
        LU = word_num(str[4:8], str[22:26])
        RD = word_num(str[8:12], str[26:30])
        RU = word_num(str[12:16], str[30:34])
        E = byte_num(str[16:18], str[34:36])
        J = byte_num(str[-6:-4], '00')

        yield LD, LU, RD, RU, E, J


# 字转化为int - check
def word_num(word, check):
    # 最高位为1  负数处理
    if int(word[0], 16) >= 8:
        # 现将除了第一位转换为数字

        # 转换为10进制数字
        result = int(word, 16)

        # 转化为源码 （按位取反后 + 1）
        result = ~result & 0xffff
        result += 1
        result = -result
    else:
        # 正数 原反补都相同
        result = int(word, 16)

    result -= int(check, 16)

    return result / 100


# 字节转化为int - check
def byte_num(byte, check):
    result = 0
    # 最高位为1  负数处理
    if int(byte[0], 16) >= 8:
        # 现将除了第一位转换为数字

        # 转换为10进制数字
        result = int(byte, 16)

        # 转化为源码 （按位取反后 + 1）
        result = ~result & 0xff
        result += 1
        result = -result
    else:
        # 正数 原反补都相同
        result = int(byte, 16)

    result -= int(check, 16)
    return result


if __name__ == '__main__':
    t = get_data_from_interface('com8')
    i = 0
    while i < 100:
        i += 1
        print(t.__next__())
