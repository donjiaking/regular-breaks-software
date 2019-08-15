#! -*- encoding=utf-8 -*-
import shutil
from PyQt5.QtGui import QPalette, QPixmap, QBrush, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QSystemTrayIcon, QMenu, QAction, qApp, QMessageBox
from PyQt5.QtCore import QTimer, Qt, QThread, QTime
import time
import sys
import os
import pygame  # 播放音乐
import random
from win32com.client import Dispatch  # 创建快捷方式
import json  # 保存用户设置
import Eyes_pop_ui
import Eyes_ui
import getpass

# 定义一些全局变量
SEC = 60  # 定义每分几秒钟的常量
interval = 0  # 定义间隔（分钟）
rest = 0  # 休息时间（分钟）
music_path = ''  # 储存播放音乐的目录
settings = {'interval': 0, 'rest': 0, 'music_path': ''}
flag = False  # 用来判断是否该结束线程，True为结束，结束后只剩下初始的主窗口线程
# 一些有关开机自动启动的路径变量
user_name = getpass.getuser()  # 获取当前用户名
target_path = 'C:\\Users\\' + user_name + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Eyes.lnk'
path_created = 'C:\\Users\\' + user_name + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Eyes2.lnk'
source_path = os.path.abspath("Eyes.exe")  # 根据文件名获取绝对路径
wDir = os.path.dirname("Eyes.exe")   # 根据文件名获取目录
# source_path = r'D:\code\python\PycharmProjects\pyqttest\dist\Eyes.exe'
# wDir = r'D:\code\python\PycharmProjects\pyqttest\dist'


class MyPop(Eyes_pop_ui.Ui_MainWindow, QMainWindow):
    """弹出窗口类，也是继承自QMainWindow"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        palette = QPalette()  # 设置背景
        palette.setBrush(QPalette.Background, QBrush(QPixmap(r"images\flower.jpg")))

        self.setPalette(palette)
        self.label.setStyleSheet("QLabel{color:white}""QLabel:hover{color:violet}")
        self.label_2.setStyleSheet("QLabel{color:rgb(209, 186, 116)}""QLabel:hover{color:yellow}")
        self.label_3.setStyleSheet("QLabel{color:rgb(209, 186, 116)}""QLabel:hover{color:white}")
        self.label_4.setStyleSheet("QLabel{color:rgb(209, 186, 116)}""QLabel:hover{color:violet}")
        self.label_5.setStyleSheet("QLabel{color:rgb(209, 186, 116)}""QLabel:hover{color:yellow}")

        self.progressBar.setStyleSheet("QProgressBar::chunk{background-color:#F4606C}""QProgressBar{border: 5px solid "
                                       "grey;border-radius: 10px;color:violet;font:75 14pt 'Comic Sans MS';}")


class MyTray(QSystemTrayIcon):
    """托盘类"""

    def __init__(self):
        super().__init__()
        self.setIcon(QIcon(r'images\eye.jpg'))  # 设置系统托盘图标
        self.setToolTip('Eyes')
        self.activated.connect(self.act)  # 设置托盘点击事件处理函数
        self.tray_menu = QMenu(QApplication.desktop())  # 创建菜单
        self.ShowAction = QAction('&show')  # 添加一级菜单动作选项(还原主窗口)
        self.QuitAction = QAction('&exit')  # 添加一级菜单动作选项(退出程序)
        self.ShowAction.triggered.connect(myrest.show)
        self.QuitAction.triggered.connect(qApp.quit)
        self.QuitAction.setToolTip('Exit the software')
        self.ShowAction.setToolTip('show the window')
        self.tray_menu.addAction(self.ShowAction)  # 为菜单添加动作
        self.tray_menu.addAction(self.QuitAction)
        self.setContextMenu(self.tray_menu)  # 设置系统托盘菜单

    def act(self, reason):
        if reason == 2 or reason == 3:  # 单击或双击
            myrest.showNormal()  # 若用show()，窗口最小化时，点击托盘图标不知为何无法显示窗口


class ProgressBar:
    """进度条类"""

    def __init__(self, pb):
        self.pb = pb

    def start(self):
        value = 0
        start_time = time.time()
        n = 100 / (rest * 60)  # 每s递增的量
        while (time.time() - start_time) <= (rest * 60):
            self.pb.setValue(value)
            value += n
            time.sleep(1)


class Music:
    """音乐类"""

    def __init__(self):
        self.li = []  # li中保存所有MP3文件的完整路径
        self.fill_li()  # 填充列表

    def fill_li(self):
        if music_path == '':
            return
        file_list = os.listdir(music_path)  # 获取指定目录下的所有文件的名称（注意包含隐藏文件），返回一个列表
        for original_file in file_list:  # 筛选掉不是mp3结尾的文件
            if original_file[-3:] != 'mp3':
                continue
            self.li.append(music_path + '\\' + original_file)

    def play(self):
        random.shuffle(self.li)  # 每次播放的顺序要不一样
        # 循环播放一首音乐
        pygame.mixer.init()
        pygame.mixer.music.load(self.li[0])
        pygame.mixer.music.play(-1)

    def stop(self):
        if pygame.mixer.music.get_busy():  # 如果还在播放，就停止
            pygame.mixer.music.stop()


class Thread(QThread):
    """线程：检测时间并做出相应反应"""

    def __init__(self):
        super().__init__()
        # 声明并初始化了此线程要用到的属性
        self.start_time = 0
        self.pop = MyPop()
        self.s = SEC
        self.m = 0

    def display_lcd(self):
        self.m = interval - 1
        self.s = SEC
        myrest.lcdNumber.display(str(interval) + ':' + '00')
        self.sleep(1)

    def update_lcd(self):
        self.s -= 1
        myrest.lcdNumber.display('{}:{:0>2d}'.format(self.m, self.s))
        if self.s == 0:
            self.s = SEC
            self.m -= 1
        self.sleep(1)

    def run(self):
        self.display_lcd()  # 显示刚开始的lcd
        music = Music()
        pb = ProgressBar(self.pop.progressBar)
        self.start_time = time.time()  # 设置刚开始的时间戳
        while not flag:
            self.update_lcd()
            if (time.time() - self.start_time) >= interval * 60:  # 若到了休息时间，则执行
                self.pop.progressBar.setValue(0)  # 重新将pb设为0，否则还是100%
                QTimer.singleShot(0, self.pop.showFullScreen)  # 用QTimer类弹出全屏的新窗口
                music.play()
                pb.start()
                music.stop()
                self.pop.hide()  # 休息完后关闭弹出的窗口
                self.start_time = time.time()  # 更新开始计时的时间戳
                self.display_lcd()  # 重设lcd


class MyRest(QMainWindow, Eyes_ui.Ui_MainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.thread = Thread()  # 初始化线程，当按下Start Looping按钮时调用此线程
        self.initUi()  # 初始化设置并开始监听事件

    def initUi(self):
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)  # 设置窗口样式
        self.setWindowIcon(QIcon(r'images\eye.jpg'))  # 设置窗口图标
        self.pushButton.setStyleSheet("QPushButton{color:black}"  # 设置按钮QSS
                                      "QPushButton:hover{color:white}"
                                      "QPushButton{background-color:red}"
                                      "QPushButton{border:2px}"
                                      "QPushButton{border-radius:10px}"
                                      "QPushButton{padding:2px 4px}")
        self.pushButton_2.setStyleSheet("QPushButton{color:black}"
                                        "QPushButton:hover{color:white}"
                                        "QPushButton{background-color:red}"
                                        "QPushButton{border:2px}"
                                        "QPushButton{border-radius:10px}"
                                        "QPushButton{padding:2px 4px}")
        self.pushButton_3.setStyleSheet("QPushButton{color:black}"
                                        "QPushButton:hover{color:white}"
                                        "QPushButton{background-color:red}"
                                        "QPushButton{border:2px}"
                                        "QPushButton{border-radius:10px}"
                                        "QPushButton{padding:2px 4px}")
        self.pushButton_4.setStyleSheet("QPushButton{color:black}"
                                        "QPushButton:hover{color:white}"
                                        "QPushButton{background-color:red}"
                                        "QPushButton{border:2px}"
                                        "QPushButton{border-radius:10px}"
                                        "QPushButton{padding:2px 4px}")
        self.pushButton_5.setStyleSheet("QPushButton{color:black}"
                                        "QPushButton:hover{color:yellow}"
                                        "QPushButton{background-color:#8CC7B5}"
                                        "QPushButton{border:2px}"
                                        "QPushButton{border-radius:10px}"
                                        "QPushButton{padding:2px 4px}")
        self.pushButton_6.setStyleSheet("QPushButton{color:black}"
                                        "QPushButton:hover{color:white}"
                                        "QPushButton{background-color:red}"
                                        "QPushButton{border:2px}"
                                        "QPushButton{border-radius:10px}"
                                        "QPushButton{padding:2px 4px}")
        self.label_3.setStyleSheet("QLabel:hover{color:violet}""QLabel{color:white}")  # 设置标签QSS
        palette = QPalette()  # 设置背景
        palette.setBrush(self.backgroundRole(),
                         QBrush(QPixmap(r"images\timg.jpg")))
        self.setPalette(palette)
        self.pushButton_2.setEnabled(False)  # 将Stop Looping按钮设置为不可点击
        if os.path.exists(path_created):  # 记住上次的选择
            self.checkBox.setChecked(True)
        self.action()  # 开始监听事件

    def action(self):
        self.pushButton.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.end)  # 结束
        self.pushButton_4.clicked.connect(self.close)  # 关闭主窗口
        self.pushButton_3.clicked.connect(self.hide)
        self.pushButton_6.clicked.connect(self.save_settings)
        self.toolButton.clicked.connect(self.browse)  # 打开对话窗口让用户选目录
        self.checkBox.clicked.connect(self.autorun)  # 如果checkBox被点击，调用self.autorun()来更新是否开机自启设置

    def start(self):
        """每次Start Looping按钮点击便调用此函数"""
        global interval, rest, flag, music_path  # 引入全局变量
        interval = self.timeEdit.time().minute()  # 获取用户输入
        rest = self.timeEdit_2.time().minute()
        music_path = self.lineEdit.text()
        if rest == 0 or interval == 0:
            return
        flag = False  # 每次start前需重设flag
        self.thread.start()  # 线程1启动
        self.pushButton.setEnabled(False)  # 更新按钮状态
        self.pushButton_2.setEnabled(True)

    def browse(self):
        global music_path
        music_path = QFileDialog.getExistingDirectory(self, 'choose a directory', r'C:\Users\don\Music',
                                                      QFileDialog.ShowDirsOnly)
        self.lineEdit.setText(music_path)

    def end(self):
        global flag
        flag = True
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(False)

    def autorun(self):
        if self.checkBox.isChecked():  # 复制basis快捷方式
            if not os.path.exists(path_created):
                shutil.copy(target_path, path_created)
        else:  # 删除快捷方式
            if os.path.exists(path_created):
                os.remove(path_created)
            else:
                pass

    def save_settings(self):
        # 获取用户输入(新的设置重启软件才有效)
        settings['interval'], settings['rest'], settings[
            'music_path'] = self.timeEdit.time().minute(), self.timeEdit_2.time().minute(), self.lineEdit.text()
        try:
            with open(r'settings.json', 'w') as f:
                json.dump(settings, f)
        except FileNotFoundError:
            QMessageBox.information(self, 'Message', 'File is Not Found !')

    def closeEvent(self, e):  # 因为退出后托盘图标不会消失（鼠标移上去才会消失），所以重写一下closeEvent
        mytray.setVisible(False)
        e.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    if not os.path.exists(target_path):  # 第一次启动程序时先创建一个快捷方式，当作basis
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(target_path)
        shortcut.Targetpath = source_path
        shortcut.WorkingDirectory = wDir
        shortcut.save()

    myrest = MyRest()
    mytray = MyTray()
    # 读取用户上一次保存的数据并显示为默认值(第一次运行之前若没有json文件，则需手动创建json文件并存入初始数据)
    with open(r'settings.json', 'r') as f:
        settings = json.load(f)
    myrest.timeEdit.setTime(QTime(0, settings['interval']))
    myrest.timeEdit_2.setTime(QTime(0, settings['rest']))
    myrest.lineEdit.setText(settings['music_path'])

    myrest.show()

    # 若以快捷方式打开（命令行会传入'-minimized'参数），则隐藏到托盘，并自动开始Loop
    if len(sys.argv) == 2 and sys.argv[1] == '-minimized':
        myrest.hide()
        myrest.pushButton.clicked.emit()

    mytray.show()

    sys.exit(app.exec_())  # THE END. 指程序一直循环运行直到主窗口被关闭终止进程（如果没有这句话，程序运行时会一闪而过）
