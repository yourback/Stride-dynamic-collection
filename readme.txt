步幅动态采集软件，使用pycharm 和 Qt desginer 完成

注意：
    1、在主文件中有一个属性名为interface_name的变量，请确保设备接入的串口名称与其相符

    2、在主文件中有一个属性名为figuresShow的变量，根据编辑其值来规定绘图内容
        例如：
            figuresShow = '1234'，显示4个图按照1234顺序从上到下排列
            figuresShow = '41'，显示2个图按照41顺序从上到下排列