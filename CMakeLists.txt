cmake_minimum_required(VERSION 3.5)

project(FHKTools)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/ShowProfile")
set(EXTENSION_CATEGORY "FHKTools")
set(EXTENSION_CONTRIBUTORS "C.Menard (FHK)")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/ShowProfile.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/ShowProfile/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(LineIntensityProfile)
add_subdirectory(HistogramLabel)
add_subdirectory(MaxProjectionFilter)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
