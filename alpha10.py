from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import matplotlib.animation as animation

from Interface import *
from UI import *
from currentview import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import matplotlib.pyplot as plt

# 设备接入的接口名称
interface_com = 'com5'

# 显示哪几个图
# 1 对应左腿
# 2 对应右腿
# 3 对应角度
# 4 对应角速度
# 5 对应大腿
# 6 对应小腿
figures = "6"

# 图像上下边界
y_axis_wid = 150
# X轴的宽度
x_axis_wid = 10


class Demo(QMainWindow, Ui_MainWindow):
    # 开始绘图的标志位
    isDrawing = False

    # 开始绘图的信号
    start_draw_signal = pyqtSignal()

    # 停止绘图的信号
    stop_draw_signal = pyqtSignal()

    # 清除图画的信号
    clear_signal = pyqtSignal(int)

    # 没有找到接入设备信号
    no_device_signal = pyqtSignal()

    # 新窗口对象
    new_view = None

    def __init__(self, parent=None):
        super(Demo, self).__init__(parent)
        self.setupUi(self)

        # 设备接入的接口名称
        self.interface_name = interface_com
        self.figuresShow = figures
        self.initUI()
        # 新建布局
        self.layout = QVBoxLayout()
        # 图
        self.mpl = MyMplCanvas(self)

        # 添加部件到布局
        self.layout.addWidget(self.mpl)

        # 布局放在画布上
        self.centralwidget.setLayout(self.layout)

        # 窗口最大化
        self.showMaximized()

        if not interface_swicth(True, self.interface_name):
            re = QMessageBox.critical(self, '错误', '请确认设备接入的接口与文档中的接口一致', QMessageBox.Yes)
            if re == QMessageBox.Yes:
                self.no_device_signal.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1:
            self.start_draw_signal.emit()
        elif event.key() == Qt.Key_F2:
            self.stop_draw_signal.emit()
        elif event.key() == Qt.Key_F3:
            self.new_view = MatplotlibWidget(self.mpl)
            self.new_view.show()

    def initUI(self):
        # 信号绑定
        self.start_draw_signal.connect(self.startWork)
        self.stop_draw_signal.connect(self.stopWork)
        self.clear_signal.connect(self.clearFigure)

        self.no_device_signal.connect(self.noDevice)
        # self.no_device_signal.connect(QCoreApplication.instance().quit)

    def startWork(self):
        if not self.isDrawing:
            self.statusbar.showMessage("当前状态：正在绘图")
            self.mpl.start_draw()
            self.isDrawing = True

    def stopWork(self):
        if self.isDrawing:
            self.statusbar.showMessage("当前状态：已经停止绘图")
            self.mpl.stop_draw()
            self.isDrawing = False

    def clearFigure(self, i):
        if self.isDrawing:
            self.statusbar.showMessage("当前状态：已经停止绘图")
            self.mpl.stop_draw()
            self.isDrawing = False

        self.mpl.clearFigures(i)

    def noDevice(self):
        sys.exit(0)


class MyMplCanvas(FigureCanvas):
    # 起始x,y的大小
    limit_x_up = 10
    limit_x_down = 0
    limit_y_up = y_axis_wid
    limit_y_down = -y_axis_wid

    # 没有设备接入的信号
    no_Device_signal = pyqtSignal()

    # 动画
    ani = None

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.figuresShow = parent.figuresShow

        # 设置中文
        plt.rcParams['font.family'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        # 新建一个绘制对象
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)

        # 设置figure布局
        self.set_figure_layout()

        if "1" in self.figuresShow:
            # build axes1
            self.axes1 = self.fig.add_subplot(self.figure1_layout)

        if "2" in self.figuresShow:
            # build axes2
            self.axes2 = self.fig.add_subplot(self.figure2_layout)

        if "3" in self.figuresShow:
            # build axes3
            self.axes3 = self.fig.add_subplot(self.figure3_layout)

        if "4" in self.figuresShow:
            # build axes4
            self.axes4 = self.fig.add_subplot(self.figure4_layout)

        if "5" in self.figuresShow:
            # build axes5
            self.axes5 = self.fig.add_subplot(self.figure5_layout)

        if "6" in self.figuresShow:
            # build axes6
            self.axes6 = self.fig.add_subplot(self.figure6_layout)

        FigureCanvas.__init__(self, self.fig)

        self.setParent(None)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        # 数据初始化
        self.Xdata, self.LDdata, self.LUdata, self.RDdata, self.RUdata, self.Edata, self.Jdata = [], [], [], [], [], [], []
        self.RD_RUdata, self.LU_LDdata = [], []
        self.RD_RU_olddata, self.LU_LD_olddata = [], []
        self.fig5_LUdata, self.fig5_RUdata = [], []
        self.fig6_LDdata, self.fig6_RDdata = [], []
        # 线条初始化
        self.LDline, self.LUline, self.Eline1, self.Jline1, self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4 = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
        # 5图的线条初始化
        self.fig5_LUline, self.fig5_RUline, self.Eline5, self.Jline5 = None, None, None, None
        # 6图的线条初始化
        self.fig6_LDline, self.fig6_RDline, self.Eline6, self.Jline6 = None, None, None, None

        # 数据源初始化
        self.data_source = get_data_from_interface()

        if "1" in self.figuresShow:
            # 图一初始化
            self.LDline, = self.axes1.plot(self.Xdata, self.LDdata, lw=1, label='左腿小腿')
            self.LUline, = self.axes1.plot(self.Xdata, self.LUdata, lw=1, label='左腿大腿')
            self.Eline1, = self.axes1.plot(self.Xdata, self.Edata, lw=1, label='工况')
            self.Jline1, = self.axes1.plot(self.Xdata, self.Jdata, lw=1, label='状态')

            self.axes1.set_ylim(self.limit_y_down, self.limit_y_up)
            self.axes1.set_xlim(self.limit_x_down, self.limit_x_up)
            self.axes1.grid(True)
            self.axes1.legend()

        if "2" in self.figuresShow:
            # 图二初始化
            self.RDline, = self.axes2.plot(self.Xdata, self.RDdata, lw=1, label='右腿小腿')
            self.RUline, = self.axes2.plot(self.Xdata, self.RUdata, lw=1, label='右腿大腿')
            self.Eline2, = self.axes2.plot(self.Xdata, self.Edata, lw=1, label='工况')
            self.Jline2, = self.axes2.plot(self.Xdata, self.Jdata, lw=1, label='状态')

            self.axes2.set_ylim(self.limit_y_down, self.limit_y_up)
            self.axes2.set_xlim(self.limit_x_down, self.limit_x_up)
            self.axes2.grid(True)
            self.axes2.legend()

        if "3" in self.figuresShow:
            # 图三初始化
            self.LU_LDline, = self.axes3.plot(self.Xdata, self.LU_LDdata, lw=1, label='左关节角度')
            self.RD_RUline, = self.axes3.plot(self.Xdata, self.RD_RUdata, lw=1, label='右关节角度')
            self.Eline3, = self.axes3.plot(self.Xdata, self.Edata, lw=1, label='工况')
            self.Jline3, = self.axes3.plot(self.Xdata, self.Jdata, lw=1, label='状态')

            self.axes3.set_ylim(self.limit_y_down, self.limit_y_up)
            self.axes3.set_xlim(self.limit_x_down, self.limit_x_up)
            self.axes3.grid(True)
            self.axes3.legend()

        if '4' in self.figuresShow:
            # 图四初始化
            self.LU_LD_oldline, = self.axes4.plot(self.Xdata, self.LU_LD_olddata, lw=1, label='左关节角速度')
            self.RD_RU_oldline, = self.axes4.plot(self.Xdata, self.RD_RU_olddata, lw=1, label='右关节角速度')
            self.Eline4, = self.axes4.plot(self.Xdata, self.Edata, lw=1, label='工况')
            self.Jline4, = self.axes4.plot(self.Xdata, self.Jdata, lw=1, label='状态')

            self.axes4.set_ylim(self.limit_y_down, self.limit_y_up)
            self.axes4.set_xlim(self.limit_x_down, self.limit_x_up)
            self.axes4.grid(True)
            self.axes4.legend()

        if '5' in self.figuresShow:
            # 图五初始化
            self.fig5_LUline, = self.axes5.plot(self.Xdata, self.LUdata, lw=1, label='左腿大腿')
            self.fig5_RUline, = self.axes5.plot(self.Xdata, self.RUdata, lw=1, label='右腿大腿')
            self.Eline5, = self.axes5.plot(self.Xdata, self.Edata, lw=1, label='工况')
            self.Jline5, = self.axes5.plot(self.Xdata, self.Jdata, lw=1, label='状态')

            self.axes5.set_ylim(self.limit_y_down, self.limit_y_up)
            self.axes5.set_xlim(self.limit_x_down, self.limit_x_up)
            self.axes5.grid(True)
            self.axes5.legend()

        if '6' in self.figuresShow:
            # 图6初始化
            self.fig6_LDline, = self.axes6.plot(self.Xdata, self.LDdata, lw=1, label='左腿小腿')
            self.fig6_RDline, = self.axes6.plot(self.Xdata, self.RDdata, lw=1, label='右腿小腿')
            self.Eline6, = self.axes6.plot(self.Xdata, self.Edata, lw=1, label='工况')
            self.Jline6, = self.axes6.plot(self.Xdata, self.Jdata, lw=1, label='状态')

            self.axes6.set_ylim(self.limit_y_down, self.limit_y_up)
            self.axes6.set_xlim(self.limit_x_down, self.limit_x_up)
            self.axes6.grid(True)
            self.axes6.legend()

    # 开始绘制
    def start_draw(self):
        if not self.ani:
            log("新建动画")
            self.ani = animation.FuncAnimation(self.fig, self.run, self.data_source, blit=True, interval=0.02,
                                               repeat=False)
        else:
            log('重复动画对象')

            self.ani.event_source.start()

        # plt.show()
        QApplication.processEvents()

    # 暂停绘制
    def stop_draw(self):
        self.ani.event_source.stop()

    # 运行绘图函数
    def run(self, data):
        if len(self.Xdata) == 0:
            t = 0
        else:
            t = self.Xdata[-1] + 0.02

        LD, LU, RD, RU, E, J = data

        # 横坐标（时间）
        self.Xdata.append(t)

        if '1' in self.figuresShow:
            # 图一
            self.LDdata.append(LD)
            self.LUdata.append(LU)

        if '2' in self.figuresShow:
            # 图二
            self.RDdata.append(RD)
            self.RUdata.append(RU)

        if '3' in self.figuresShow:
            # 图三
            self.LU_LDdata.append(LU - LD)
            self.RD_RUdata.append(RD - RU)

        if '4' in self.figuresShow:
            # 图四
            self.LU_LD_olddata.append((LU - LD) if len(self.LU_LD_olddata) == 0 else (LU - LD - self.LU_LD_olddata[-1]))
            self.RD_RU_olddata.append((RD - RU) if len(self.RD_RU_olddata) == 0 else (RD - RU - self.RD_RU_olddata[-1]))

        if '5' in self.figuresShow:
            # 图五
            self.fig5_LUdata.append(LU)
            self.fig5_RUdata.append(RU)
        if '6' in self.figuresShow:
            # 图6
            self.fig6_LDdata.append(LD)
            self.fig6_RDdata.append(RD)

        # 标志位
        self.Edata.append(E)
        self.Jdata.append(J)

        # 更新绘图坐标系的横轴
        self.update_xmax(t)

        # 更新每条线的数据
        self.update_linedata()

        resultTuple = ()
        fig1Tuple = (self.LDline, self.LUline, self.Eline1, self.Jline1)
        fig2Tuple = (self.RDline, self.RUline, self.Eline2, self.Jline2)
        fig3Tuple = (self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3)
        fig4Tuple = (self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4)
        fig5Tuple = (self.fig5_LUline, self.fig5_RUline, self.Eline5, self.Jline5)
        fig6Tuple = (self.fig6_LDline, self.fig6_RDline, self.Eline6, self.Jline6)

        if self.LDline:
            resultTuple += fig1Tuple
        if self.RDline:
            resultTuple += fig2Tuple
        if self.LU_LDline:
            resultTuple += fig3Tuple
        if self.LU_LD_oldline:
            resultTuple += fig4Tuple
        if self.fig5_LUline:
            resultTuple += fig5Tuple
        if self.fig6_LDline:
            resultTuple += fig6Tuple

        return resultTuple

        # 根据用户填写的图数字，显示图像
        # if len(self.figuresShow) == 5:
        #     # 12345
        #     return (
        #         self.LDline, self.LUline, self.Eline1, self.Jline1, self.RDline, self.RUline, self.Eline2, self.Jline2,
        #         self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3, self.LU_LD_oldline, self.RD_RU_oldline,
        #         self.Eline4, self.Jline4, self.fig5_LUline, self.fig5_RUline, self.Eline5, self.Jline5)
        # elif len(self.figuresShow) == 4:
        #     # 1234
        #     if not self.fig5_LUline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4
        #     # 2345
        #     if not self.LDline:
        #         return self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4, self.fig5_LUline, self.fig5_RUline, self.Eline5, self.Jline5
        #     # 1345
        #     elif not self.RDline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4, self.fig5_LUline, self.fig5_RUline, self.Eline5, self.Jline5
        #     # 1245
        #     elif not self.LU_LDline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4, self.fig5_LUline, self.fig5_RUline, self.Eline5, self.Jline5
        #     # 1235
        #     elif not self.LU_LD_oldline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3, self.fig5_LUline, self.fig5_RUline, self.Eline5, self.Jline5
        # elif len(self.figuresShow) == 3:
        #     # 234
        #     if not self.LDline:
        #         return self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4
        #     # 134
        #     elif not self.RDline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4
        #     # 124
        #     elif not self.LU_LDline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4
        #     # 123
        #     elif not self.LU_LD_oldline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3
        # elif len(self.figuresShow) == 2:
        #     # 12
        #     if self.LDline and self.RDline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.RDline, self.RUline, self.Eline2, self.Jline2
        #     # 13
        #     elif self.LDline and self.LU_LDline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3
        #     # 14
        #     elif self.LDline and self.LU_LD_oldline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4
        #     # 15
        #     elif self.LDline and self.fig5_LUline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1, self.fig5_LUline, self.fig5_RUline, self.Eline5, self.Jline5
        #     # 23
        #     elif self.RDline and self.LU_LDline:
        #         return self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3
        #     # 24
        #     elif self.RDline and self.LU_LD_oldline:
        #         return self.RDline, self.RUline, self.Eline2, self.Jline2, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4
        #     # 34
        #     elif self.LU_LDline and self.LU_LD_oldline:
        #         return self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3, self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4
        # elif len(self.figuresShow) == 1:
        #     if self.LDline and self.LUline:
        #         return self.LDline, self.LUline, self.Eline1, self.Jline1
        #     elif self.RDline and self.RUline:
        #         return self.RDline, self.RUline, self.Eline2, self.Jline2
        #     elif self.LU_LDline and self.RD_RUline:
        #         return self.LU_LDline, self.RD_RUline, self.Eline3, self.Jline3
        #     elif self.LU_LD_oldline and self.RD_RU_oldline:
        #         return self.LU_LD_oldline, self.RD_RU_oldline, self.Eline4, self.Jline4
        #     elif self.fig5_LUline and self.fig5_RUline:
        #         return self.fig5_LUline, self.fig5_RUline, self.Eline5, self.Jline5

    # 更新每条线的数据
    def update_linedata(self):
        """更新每条线的数据"""
        if '1' in self.figuresShow:
            # 图一
            self.LDline.set_data(self.Xdata, self.LDdata)
            self.LUline.set_data(self.Xdata, self.LUdata)
            self.Eline1.set_data(self.Xdata, self.Edata)
            self.Jline1.set_data(self.Xdata, self.Jdata)
        if '2' in self.figuresShow:
            # 图二
            self.RDline.set_data(self.Xdata, self.RDdata)
            self.RUline.set_data(self.Xdata, self.RUdata)
            self.Eline2.set_data(self.Xdata, self.Edata)
            self.Jline2.set_data(self.Xdata, self.Jdata)
        if '3' in self.figuresShow:
            # 图三
            self.LU_LDline.set_data(self.Xdata, self.LU_LDdata)
            self.RD_RUline.set_data(self.Xdata, self.RD_RUdata)
            self.Eline3.set_data(self.Xdata, self.Edata)
            self.Jline3.set_data(self.Xdata, self.Jdata)
        if '4' in self.figuresShow:
            # 图四
            self.LU_LD_oldline.set_data(self.Xdata, self.LU_LD_olddata)
            self.RD_RU_oldline.set_data(self.Xdata, self.RD_RU_olddata)
            self.Eline4.set_data(self.Xdata, self.Edata)
            self.Jline4.set_data(self.Xdata, self.Jdata)

        if '5' in self.figuresShow:
            # 图五
            self.fig5_LUline.set_data(self.Xdata, self.fig5_LUdata)
            self.fig5_RUline.set_data(self.Xdata, self.fig5_RUdata)
            self.Eline5.set_data(self.Xdata, self.Edata)
            self.Jline5.set_data(self.Xdata, self.Jdata)

        if '6' in self.figuresShow:
            self.fig6_LDline.set_data(self.Xdata, self.fig6_LDdata)
            self.fig6_RDline.set_data(self.Xdata, self.fig6_RDdata)
            self.Eline6.set_data(self.Xdata, self.Edata)
            self.Jline6.set_data(self.Xdata, self.Jdata)

    # 清除已绘图像
    def clearFigures(self, i):
        pass

    # 根据用户写的figuresShow设置图的位置
    def set_figure_layout(self):
        """根据用户写的figuresShow设置图的位置"""
        figure_count = len(self.figuresShow)

        for i, f in enumerate(self.figuresShow):
            if f == '1':
                # 511
                self.figure1_layout = str(figure_count) + '1' + str(i + 1)
            elif f == '2':
                # 512
                self.figure2_layout = str(figure_count) + '1' + str(i + 1)
            elif f == '3':
                # 513
                self.figure3_layout = str(figure_count) + '1' + str(i + 1)
            elif f == '4':
                # 514
                self.figure4_layout = str(figure_count) + '1' + str(i + 1)
            elif f == '5':
                # 515
                self.figure5_layout = str(figure_count) + '1' + str(i + 1)
            elif f == '6':
                # 616
                self.figure6_layout = str(figure_count) + '1' + str(i + 1)

    # 更新绘图坐标系的横轴
    def update_xmax(self, t):
        """更新绘图坐标系的横轴"""
        # xmin = 0

        xmax = 100

        if '1' in self.figuresShow:
            xmin, xmax = self.axes1.get_xlim()
        elif '2' in self.figuresShow:
            xmin, xmax = self.axes2.get_xlim()
        elif '3' in self.figuresShow:
            xmin, xmax = self.axes3.get_xlim()
        elif '4' in self.figuresShow:
            xmin, xmax = self.axes4.get_xlim()
        elif '5' in self.figuresShow:
            xmin, xmax = self.axes5.get_xlim()
        elif '6' in self.figuresShow:
            xmin, xmax = self.axes6.get_xlim()

        if t >= xmax:
            if '1' in self.figuresShow:
                # self.axes1.set_xlim(xmin, 2 * xmax)
                self.axes1.set_xlim(xmax, xmax + x_axis_wid)
                self.axes1.figure.canvas.draw()
            if '2' in self.figuresShow:
                # self.axes2.set_xlim(xmin, 2 * xmax)
                self.axes2.set_xlim(xmax, xmax + x_axis_wid)
                self.axes2.figure.canvas.draw()
            if '3' in self.figuresShow:
                # self.axes3.set_xlim(xmin, 2 * xmax)
                self.axes3.set_xlim(xmax, xmax + x_axis_wid)
                self.axes3.figure.canvas.draw()
            if '4' in self.figuresShow:
                # self.axes4.set_xlim(xmin, 2 * xmax)
                self.axes4.set_xlim(xmax, xmax + x_axis_wid)
                self.axes4.figure.canvas.draw()
            if '5' in self.figuresShow:
                # self.axes5.set_xlim(xmin, 2 * xmax)
                self.axes5.set_xlim(xmax, xmax + x_axis_wid)
            if '6' in self.figuresShow:
                # self.axes6.set_xlim(xmin, 2 * xmax)
                self.axes6.set_xlim(xmax, xmax + x_axis_wid)

        QApplication.processEvents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Demo()
    win.show()
    sys.exit(app.exec_())
