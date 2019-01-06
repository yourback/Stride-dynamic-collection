from PyQt5.QtWidgets import QApplication, QVBoxLayout, QSizePolicy, QWidget
from numpy import arange
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import sys


# 静态可拖动图
class HistoryInfo(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        # 设置中文
        plt.rcParams['font.family'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        # 新建一个绘制对象
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)

        self.figuresShow = parent.figuresShow

        if "1" in self.figuresShow:
            # build axes1
            self.axes1 = self.fig.add_subplot(parent.figure1_layout)

        if "2" in self.figuresShow:
            # build axes2
            self.axes2 = self.fig.add_subplot(parent.figure2_layout)

        if "3" in self.figuresShow:
            # build axes3
            self.axes3 = self.fig.add_subplot(parent.figure3_layout)

        if "4" in self.figuresShow:
            # build axes4
            self.axes4 = self.fig.add_subplot(parent.figure4_layout)

        if '5' in self.figuresShow:
            # build axes5
            self.axes5 = self.fig.add_subplot(parent.figure5_layout)

        FigureCanvas.__init__(self, self.fig)

        self.setParent(None)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def start_static_plot(self, parent):

        alist, blist, elist, flist = parent.LDdata, parent.LUdata, parent.Edata, parent.Jdata

        clist, dlist = parent.RDdata, parent.RUdata

        a_blist, c_dlist = parent.LU_LDdata, parent.RD_RUdata

        a_b_oldlist, c_d_oldlist = parent.LU_LD_olddata, parent.RD_RU_olddata

        t = arange(0, len(alist) * 0.02, 0.02)

        if "1" in self.figuresShow:
            # 图1
            self.LDline, = self.axes1.plot(t, alist, '-', label='左腿小腿')
            self.LUline, = self.axes1.plot(t, blist, '-', label='左腿大腿')
            self.Eline1, = self.axes1.plot(t, elist, '-', label='工况')
            self.Jline1, = self.axes1.plot(t, flist, '-', label='状态')
            self.axes1.grid(True)
            self.axes1.legend()

        if "2" in self.figuresShow:
            # 图2
            self.RDline, = self.axes2.plot(t, clist, '-', label='右腿小腿')
            self.RUline, = self.axes2.plot(t, dlist, '-', label='右腿大腿')
            self.Eline2, = self.axes2.plot(t, elist, '-', label='工况')
            self.Jline2, = self.axes2.plot(t, flist, '-', label='状态')
            self.axes2.grid(True)
            self.axes2.legend()

        if "3" in self.figuresShow:
            # 图3
            self.LU_LDline, = self.axes3.plot(t, a_blist, '-', label='左关节角度')
            self.RD_RUline, = self.axes3.plot(t, c_dlist, '-', label='右关节角度')
            self.Eline3, = self.axes3.plot(t, elist, '-', label='工况')
            self.Jline3, = self.axes3.plot(t, flist, '-', label='状态')
            self.axes3.grid(True)
            self.axes3.legend()

        if "4" in self.figuresShow:
            # 图4
            self.LU_LD_oldline, = self.axes4.plot(t, a_b_oldlist, '-', label='左关节角速度')
            self.RD_RU_oldline, = self.axes4.plot(t, c_d_oldlist, '-', label='右关节角速度')
            self.Eline4, = self.axes4.plot(t, elist, '-', label='工况')
            self.Jline4, = self.axes4.plot(t, flist, '-', label='状态')
            self.axes4.set_xlabel('time(s)')
            self.axes4.grid(True)
            self.axes4.legend()

        if '5' in self.figuresShow:
            # 图5
            self.fig5_LUline, = self.axes5.plot(t, blist, '-', label='左腿大腿')
            self.fig5_RUline, = self.axes5.plot(t, dlist, '-', label='右腿大腿')
            self.Eline5, = self.axes5.plot(t, elist, '-', label='工况')
            self.Jline5, = self.axes5.plot(t, flist, '-', label='状态')
            self.axes5.grid(True)
            self.axes5.legend()


class MatplotlibWidget(QWidget):

    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(None)

        self.setWindowTitle(parent.figuresShow)

        self.parent = parent

        self.initUi()

        self.m.start_static_plot(self.parent)

    def initUi(self):
        self.layout = QVBoxLayout(self)
        self.m = HistoryInfo(self.parent)

        self.m_n = NavigationToolbar(self.m, self)

        self.layout.addWidget(self.m, 1)
        self.layout.addWidget(self.m_n, 1)

        self.showMaximized()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MatplotlibWidget()
    # ui.mpl.start_static_plot()

    ui.show()
    sys.exit(app.exec_())
