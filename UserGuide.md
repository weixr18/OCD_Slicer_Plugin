# Open COVID Detector 用户指南

## 1 环境要求

+ 操作系统：windows10 64 bit 或 windows10 32 bit
+ 内存：建议大于8GB

## 2 安装方法

+ 下载项目压缩包 OCD_Slicer_Plugin_xxx.rar
+ 将压缩包解压到磁盘中某一位置
    + 建议解压到Slicer安装目录下的lib/Slicer-4.10/qt-scripted-modules/OCD_Slicer_Plugin_xxx/，便于寻找。
    + 注意：**路径中不能含有中文！！**
+ 进入Tools/python/文件夹，根据系统位数，将相应rar文件解压到同名文件夹
    + 若为32位系统，右键单击python-3.6.2-embed-win32.rar，选择“解压到python-3.6.2-embed-win32\”
    + 若为64位系统，右键单击python-3.6.2-embed-amd64.rar，选择“解压到python-3.6.2-embed-amd64\”
+ 启动Slicer，添加插件
    + 在插件下拉列表中选择“Extension Wizard”插件
    + 点击“Select Extention”
    + 进入刚才解压的OCD_Slicer_Plugin_xxx/文件夹，选中里面的OpenCOVID_Detecter文件夹，点击确定。
    + 若插件启动后，python控制台无红色报错，且弹出黑色窗口显示“Initialize success.”，则说明安装完成。
    + 若有任何报错或异常情况（崩溃、闪退、插件界面加载不出来等），请联系开发人员。

## 3 使用指南

等待前端撰写......

