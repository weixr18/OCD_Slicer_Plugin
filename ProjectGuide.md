# OCD_Slicer_Plugin 项目概览

## 1 简介

OCD_Slicer_Plugin是一个slicer插件项目，通过对识别病人肺部CT图像的分析，实现新冠肺炎(COVID-19)的检测。

项目贡献者：魏欣然，陈炜翔，门恺文，韩沛轶，刘博伦

## 2 分支说明

本分支为windows64位系统的release分支。
若要**安装**，请参考UserGuide.md

## 3 项目结构

项目主要文件均在OpenCOVID_Detecter目录下。下面是这个目录的结构和模块功能简介。

    -CT_Detect/

    CT检测插件模块，目前唯一的模块。
    模块从Slicer导入病人CT图像，进行切片——分割——评分后，将结果显示在前端界面上，辅助医生进行新冠肺炎诊断。

    实现方式：
    插件加载时，后端服务器进程（python3.6）待命。
    开始按钮点击后，前端通过socket将CT体数据（numpy数组）传递给后端进程。后端基于pytorch，逐切片进行深度神经网络分类。分类完毕后，将分类结果同样通过socket传回前端，在Slicer界面上进行展示。

        --Batch/
        独立批处理工具。可一次处理多组dicom格式原始数据。

            --batch_GUI_py3.py
            批处理数据图形界面，qt自动生成

            --batch_main_py3.py
            批处理工具前端，主函数

            --batch_process_py3.py
            批处理工具后端，具体的处理流程。实质上和slicer插件后端相同。

            --Batch_GUI.ui
            批处理工具界面设计文件

        --Front/
        slicer插件python2部分（前端）其他组件。

            --data_front.py
            前端数据处理操作。目前仅有分割插值部分。

        --Old/
        弃用代码

            --grad_cam_py3.py
            生成热图的实现文件。输入判断为正类的体数据切片，输出每张切片对应的热图。

        --Resources/
        各类资源文件，包括前端ui设计文件

            --Icons/
            图标

            --UI/
            Slicer前端界面设计文件

        --Testing/
        测试脚本。目前无。
        
        --Utils/
        后端组件库。后端所有实现代码均在此文件夹下。

            --data_py3.py
            进行数据预处理，包括大小调整、范围调整、切片等

            --segment_py3.py
            对每个切片生成肺分割。目前采用简单阈值+连通域算法，对大块肺边缘病变不稳定。

            --detect_py3.py
            对每个切片进行CT分类。输入为CT切片和对应的mask（即分割）。

            ---net2d_py3.py
            各种卷积网络模型。目前使用其中的resnet152作为分类网络。（resnet，残差网络，2015年由KaiMing He等提出。）

        
        --CT_Detect.py
        前端和前后端接口文件。

            Client
            客户端通信类。具体通信的实现。

            CT_DetectWidget
            插件模块窗口类，MVC中的View。负责GUI展示、用户交互，即前端。

            CT_DetectLogic
            插件模块逻辑类。MVC中的Control。在Client和Widget间传递参数。

        --server_py3.py
        后端服务器。负责与前端通信、调用各后端模块功能。       

        --CMakeLists.txt
        C++项目构建的时候的make命令。目前无用。

    -model/
    训练好的神经网络模型权重。


