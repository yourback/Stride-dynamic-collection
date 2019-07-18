# coding=gb18030

import threading
import time
import serial

from Interface import word_num, byte_num
from printutil import log


class ComThread:
    def __init__(self, Port='COM8'):
        self.l_serial = None
        self.alive = False
        self.waitEnd = None
        self.port = Port
        self.ID = None
        self.data = None

    def waiting(self):
        if not self.waitEnd is None:
            self.waitEnd.wait()

    def SetStopEvent(self):
        if not self.waitEnd is None:
            self.waitEnd.set()
        self.alive = False
        self.stop()

    def start(self):
        self.l_serial = serial.Serial()
        self.l_serial.port = self.port
        self.l_serial.baudrate = 115200
        self.l_serial.timeout = 2
        self.l_serial.open()
        if self.l_serial.isOpen():
            self.waitEnd = threading.Event()
            self.alive = True
            self.thread_read = None
            self.thread_read = threading.Thread(target=self.FirstReader)
            self.thread_read.setDaemon(1)
            self.thread_read.start()
            return True
        else:
            return False

    def SendDate(self, i_msg, send):
        lmsg = ''
        isOK = False
        if isinstance(i_msg):
            lmsg = i_msg.encode('gb18030')
        else:
            lmsg = i_msg
        try:
            # 发送数据到相应的处理组件
            self.l_serial.write(send)
        except Exception as ex:
            pass;
        return isOK

    def FirstReader(self):
        while self.alive:
            time.sleep(0.1)

            data = ''
            data = data.encode('utf-8')

            n = self.l_serial.inWaiting()
            if n:
                data = data + self.l_serial.read(n)
                log('get data from serial port:', data)
                log(type(data))

            n = self.l_serial.inWaiting()
            if len(data) > 0 and n == 0:
                try:
                    temp = data.decode('gb18030')
                    log(type(temp))
                    log(temp)
                    car, temp = str(temp).split("\n", 1)
                    log(car, temp)

                    string = str(temp).strip().split(":")[1]
                    str_ID, str_data = str(string).split("*", 1)

                    log(str_ID)
                    log(str_data)
                    log(type(str_ID), type(str_data))

                    if str_data[-1] == '*':
                        break
                    else:
                        log(str_data[-1])
                        log('str_data[-1]!=*')
                except:
                    log("读卡错误，请重试！\n")

        self.ID = str_ID
        self.data = str_data[0:-1]
        self.waitEnd.set()
        self.alive = False

    def stop(self):
        self.alive = False
        self.thread_read.join()
        if self.l_serial.isOpen():
            self.l_serial.close()


# 调用串口，测试串口
def main():
    rt = ComThread()
    rt.sendport = '**1*80*'
    try:
        if rt.start():
            log(rt.l_serial.name)
            rt.waiting()
            log("The data is:%s,The Id is:%s" % (rt.data, rt.ID))
            rt.stop()
        else:
            pass
    except Exception as se:
        log(str(se))

    if rt.alive:
        rt.stop()

    log('')
    log('End OK .')
    temp_ID = rt.ID
    temp_data = rt.data
    del rt
    return temp_ID, temp_data


if __name__ == '__main__':
    # 设置一个主函数，用来运行窗口，便于若其他地方下需要调用串口是可以直接调用main函数
    # ID, data = main()
    #
    # print("******")
    # print(ID, data)
    str = ' FF E5 FF E5 FF C9 00 3C 00 00 00 00 00 00 00 00 00 00 00 58 FF 85 FF A8 00 B2 00 00 00 00 00 00 00 00 00 0D 0A[2018-09-17 05:33:20.648]'.replace(
        ' ', '')
    str = str[:str.rindex('[')]
    log(str)
    LD = word_num(str[0:4], str[18:22])
    log(LD)
    LU = word_num(str[4:8], str[22:26])
    log(LU)
    RD = word_num(str[8:12], str[26:30])
    log(RD)
    RU = word_num(str[12:16], str[30:34])
    log(RU)
    E = byte_num(str[16:18], str[34:36])
    log(E)
    J = byte_num(str[-6:-4], '00')
    log(J)
    # print('LD:%s,LU:%s,RD:%s,RU:%s,E:%s,J:%s' % (LD, LU, RD, RU, E, J))
