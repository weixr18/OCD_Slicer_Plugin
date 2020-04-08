cmake_minimum_required(VERSION 3.5)

project(OpenCOVID_Detecter)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/OpenCOVID_Detecter")
set(EXTENSION_CATEGORY "Diagnose")
set(EXTENSION_CONTRIBUTORS "Xinran Wei (Tsinghua.University.)")
set(EXTENSION_DESCRIPTION "An COVID-19 Auxiliary Diagnostic Toolkit")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/OpenCOVID_Detecter.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/OpenCOVID_Detecter/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(CT_Detect)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
