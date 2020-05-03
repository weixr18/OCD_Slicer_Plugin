# OCD_Slicer_Plugin
A plugin of Slicer to help diagnose COVID-19 

## Project description

This is a Slicer open source plugin for the detection of COVID-19-induced pneumonia. 

The principle is based on a deep learning technique for scanning CT identification of the patient's lungs. 

So far, we have implemented a prototype version of the plugin. In this version, we can handle the corpora data that Slicer reads in. We section it, perform lung segmentation, and use the segmentation results and sections to diagnose the presence or absence of COVID-19 lesions on this CT image.

Our algorithms are still being tested and optimized. After the algorithm has matured steadily, we will make it part of the Slicer open source plugin library.
