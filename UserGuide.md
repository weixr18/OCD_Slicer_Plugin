# Open COVID Detector 用户指南

## 1 环境要求

+ 操作系统：windows10 64 bit
+ 内存：建议大于8GB
+ 附：win10系统查看位数方法
    + 在桌面上右键单击“此电脑”，点击“属性”
    + 在系统-系统类型中可看到系统是否为64位，以及内存大小。

## 2 安装方法

+ 下载项目压缩包 OCD_Slicer_Plugin_amd64.rar
    + 链接：https://cloud.tsinghua.edu.cn/d/b0e04aeb0dc64b67977a/
    + 备注：清华校内ip下载较快
+ 将压缩包解压到磁盘中某一位置
    + 右键单击压缩包，选择“**解压到OCD_Slicer_Plugin_amd64\\**”
    + 建议解压到Slicer安装目录下的lib/Slicer-4.10/qt-scripted-modules/OCD_Slicer_Plugin_amd64/，便于寻找。
    + 注意：**路径中不能含有中文！！**
+ 进入Tools/python/文件夹，根据系统位数，将相应rar文件解压到当前文件夹
    + 右键单击python-3.6.2-embed-amd64.rar，选择“**解压到当前文件夹**”
+ 启动Slicer，添加插件
    + 在插件下拉列表中找到“Developer Tools”，选择里面的“Extension Wizard”插件
    + 点击“Select Extention”
    + 进入刚才解压的OCD_Slicer_Plugin_xxx/文件夹，选中里面的OpenCOVID_Detecter文件夹，点击确定。
    + 在插件下拉列表里找到“COVID Detect”分组，点击“CT_Detect”启动插件
    + 若插件启动后，Slicer中的python控制台无红色报错行，且弹出的黑色窗口中显示“Loading... Initialize success.”，则说明安装成功。
    + 若出现下列错误：
        SystemError: D:\D\S\Slicer-4102-build\Python-2.7.13\Objects\classobject.c:521: bad argument to internal function
      则为正常现象，不影响使用。
    + 若有任何其他报错或异常情况（崩溃、闪退、插件界面加载不出来等），请联系开发人员。

## 3 使用指南

等待前端撰写......

