# 用PyQt制作定时提醒休息的小软件

## PyQt5配置教程
- https://www.jianshu.com/p/c61fc80ad6b3
- https://www.jianshu.com/p/5b063c5745d0

## PyQt5知识点
- https://zhuanlan.zhihu.com/p/28287825
- http://code.py40.com/1961.html
- https://www.bilibili.com/video/av54310770?from=search&seid=4096965450837428342

## 实战：用PyQt5制作定时休息软件
python和pyqt5学了几天后，为了保护日薄西山的眼睛，并学以致用，便想到自己做一个定时休息软件。于是便花两天时间写出了这个代码，可是功能
简陋，代码混乱。

### 主要功能

- 可以隐藏到托盘
- 可以让用户选择是否开机自动启动
- 可以保存用户设置，下次重启软件时自动将设置值作为默认值
- 主窗口显示还剩多少时间休息的倒计时
- 时间到了后弹出一个全屏覆盖的子窗口
- 窗口弹出后音乐（音乐目录的路径由用户选择）自动播放，休息完后自动停止
- 弹出窗口的进度条实现
- 一直循环直到用户按下Stop Looping按钮

### 界面图片

### 最终代码
我先是用Qtdesigner搭好基础界面，并将ui文件转换为py文件，即Eyes_pop_ui.py和Eyes_ui.py，再用以下代码实现所有逻辑和界面美化。

[include](D:\code\python\PycharmProjects\pyqttest\Eyes.py)

### 注意点
#### 播放音乐
- pygame.init() 进行全部模块的初始化，
- pygame.mixer.init() 或者只初始化音频部分
- pygame.mixer.music.load('xx.mp3') 使用文件名作为参数载入音乐 ,音乐可以是ogg、mp3等格式。载入的音乐不会全部放到内容中，而是以流的形式播放的，即在
播放的时候才会一点点从文件中读取，一次只能载一个
- pygame.mixer.music.play()播放载入的音乐，假如里面有数字n是说明播放n+1次（即播放一次后循环n次,若-1即循环播放）。该函数立即返回，音乐播放在后台进行
- pygame.mixer.music.stop() 停止播放
- pygame.mixer.music.pause() 暂停播放
- pygame.mixer.music.unpause() 取消暂停
- pygame.mixer.music.queue('xx.mp3') 将音乐文件加入队列，等当前音乐播放完后自动播放，注意排队等待的音乐文件只能有一个（为什么我加上去不会播放...我
只能单曲循环了）
- pygame.mixer.quit() 退出音乐播放
- 还试了导入from win32com.client import Dispatch，然后用COM组件打开Windows Media Player：
```python
mp = Dispatch("WMPlayer.OCX")  # 遗憾的是，这一行发生了错误...
tune = mp.newMedia("..path..")
mp.currentPlaylist.appendItem(tune)
mp.controls.play()
mp.controls.stop()
```
- 注：还可用pyglet pyaudio playsound等模块。

#### 设置窗口背景
- 最简单：用QSS样式表的方式设置窗口背景，这种方法会让所有子控件都继承
` self.setStyleSheet("MainWindow{border-image:url(..path..)}")`
- QPallete：
```python
palette = QPalette()
palette.setBrush(QPalette.Background, QBrush(QPixmap("..path..")))
win.setPalette(palette)
```
当背景图片的宽度高度大于窗口的宽度高度时，背景图片会平铺整个背景; 当背景图片宽度高度小于窗口的宽度高度时，则会加载多个背景图片 
- 重写窗体对象的paintEvent()方法：
```python
def paintEvent(self, event):
        painter = QPainter(self)
        # 设置背景颜色
        painter.setBrush(Qt.green)
        painter.drawRect(self.rect())
        # 设置背景图片，平铺到整个窗口，随着窗口改变而改变
        # pixmap = QPixmap(r"..path..")
        # painter.drawPixmap(self.rect(), pixmap)
```

#### 用Python隐藏和显示windows任务栏：
虽然没用到（本来是为了全屏），但既然了解了还是在此记录一下。

1. 下载pywin32模块，此模块封装了部分windowsAPI。手动下载（python3.7以上无法pip）：`https://github.com/mhammond/pywin32/releases`我的是
pywin32-224.win32-py3.6.exe。若下载时无法识别正确路径，注意选择版本，可能python版本和pywin32版本不匹配。
2. 
```python 
import win32gui
fd = win32gui.FindWindow("Shell_TrayWnd",None) # 任务栏类名为Shell_TrayWnd
win32gui.ShowWindow(fd,0) # SW_HIDE = 0
win32gui.ShowWindow(fd,5) # SW_SHOW = 5
```

#### 获取当前用户名
```python
import getpass
user_name = getpass.getuser()
```

#### 如何保存用户设置
- 保存用户数据：用json模块，用户点击Save Settings按钮时便把数据保存进json文件，当用户打开软件时，将json里面的数据读出，从而自动显示保存值作为默认值

#### 最小化到托盘
创建一个托盘类，继承自QSystemTrayIcon，详见代码

#### 如何开机自动启动
这方面我不太会...我用了一个蹩脚的办法：

首次运行程序时，程序会在windows的C:\Users\username\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup目录下创建一个当作“basis”的Eye
s.lnk快捷方式，然后手动修改快捷方式的属性（怎么也找不到可以将文件的目标添加另一个参数的方法），将目标改为 "..path.." -minimized ，这样打开此快捷方式
的时候，便会向程序传入两个命令行参数，用sys.argv获取，若第二个的参数是-minimized，则自动隐藏到托盘，这样就可以实现开机自动启动并隐藏到托盘的功能了。

但是，我们要让用户自己选择，也就意味着要删除和创建这个Eyes.lnk，然鹅它是basis，是不能动它的，因为删除后它“目标”里面的内容就跑掉了。于是在用户打上开机
自启的checkbox的√时，我让程序复制那个basis，生成Eyes2.lnk就好了，取消√就删除它。这里我用shutil.copy()方法复制，用os.move()删除。这种方法好stupid。

#### 在别的（Windows系统）电脑上运行方法
- 打包后：需在第一次运行时找到创建的Eyes.lnk然后修改其“目标”属性，在路径后加一个空格再加上-minimized即可；注意images文件夹、setting.json和Eyes.exe
需放在同一目录下。
- 若未打包：需修改代码中的一些路径才能正常运行。

#### 其它
- 为了防止和字符串本身的引号冲突，使用 \ 来转义，一般情况下这个也不会引起什么问题，但是当你要使用 \ 来转义 \ 的时候，就比较混乱了，比如我们想要输出一
个 \ ，得写两个 \ ，否则会报语法错误，因为 \ 把后面的引号给转义了，必须使用 \
- 获取目录下所有文件的方法：用allpath = os.listdir(path); os.listdir()返回指定路径下所有的文件和文件夹列表,但是子目录下文件不遍历
- 关于打包：
1. pyinstaller -F -w Eyes.py Eyes_pop_ui.py Eyes_ui.py -i dist/images/eye.ico
2. 需将相关资源（json、txt、img）放到dist目录下（不知为何用绝对路径也要放到这个目录下），否则exe文件无法执行，弹出“Failed to execute Eyes script”。
我找了好久的原因，比如可能要用--hidden-import导入隐藏包，还有可能pyinstaller打包参数不对...最后发现原因只是json文件没放到dist目录下...
3. pyinstaller打包坑是相当的多
4. 打包后会在build和dist目录下生成相应文件，build文件夹保存的是临时文件目录可以安全删除，最终的打包程序在dist文件夹中
- 一开始，弹出窗口自动关闭后，程序会不正常退出, 考虑到动态语言多线程的不稳定性，我去掉了两个线程（原来用了好几个线程，发现其实没必要）后便不会异常退出
了。


20190809
