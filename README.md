# Real-time-Motion-Correction-Plug-In

![logo](https://user-images.githubusercontent.com/44628918/166712172-ba85c63d-27d2-47cd-b3fa-ba052acedbef.png)

**How to use it ?**
1、Run the software as follows
 ![1](https://user-images.githubusercontent.com/44628918/166712681-7ce77177-7ba8-422d-b686-e8e0fadbe108.png)
2、Initialize the environment, select the template file
![1651677209(1)](https://user-images.githubusercontent.com/44628918/166713031-52582c40-8120-4041-a2eb-473cb132de76.png)
3、Select video data awaiting motion correction
![image](https://user-images.githubusercontent.com/44628918/166713330-a927ebaf-8660-47b6-8ca4-b563ca468728.png)
4、Open the real-time calibration interface
![image](https://user-images.githubusercontent.com/44628918/166713430-e87a1d70-f5b5-4086-beb9-a0b97b94b376.png)
5、Click the start button to perform real-time motion correction of the image
![image](https://user-images.githubusercontent.com/44628918/166713649-4cc5615d-bfa4-4a98-8e0c-e90033b4f73d.png)

**Software Environment Construction Guide**
1、	Install anaconda
2、	Install the GPU driver and the corresponding cuda version. For example: GTX1060 driver and cuda 10.2
3、	Open pytorch.org and use conda to install the corresponding version. For example: conda install pytorch==1.7.0 torchvision==0.8.0 torchaudio==0.7.0 cudatoolkit=10.2 -c pytorch
4、	Install Pycharm, note that the configuration environment is Python in the anaconda directory
5、	Use Pycharm to test registration.py, if the operation is successful, the Pytorch environment configuration is successful
6、	Copy the compiled version of OpenCV corresponding to mingw64, for example: opencv3.43_mingw_64
7、	Add system environment variable: MinGW 64-bit version
For example: C:\opencv3.43_mingw_64\install\x64\mingw\bin
8、	Install the corresponding version of Qt, such as Qt 5.12.8
9、	Click the .pro file to open the project, and select the Qt corresponding MINGW 64 compiler
10、	Change the opencv and python paths in the .pro file as follows

#Environment opencv3.43_mingw_64
INCLUDEPATH += D:\ProgramData\opencv3.43_mingw_64\install\include
LIBS += -L D:\ProgramData\opencv3.43_mingw_64\install\x64\mingw\lib\libopencv_*.a \

**#python enviroment**
INCLUDEPATH += 'D:\ProgramData\Anaconda3\include'
INCLUDEPATH += 'D:\ProgramData\Anaconda3\Lib\site packages\numpy\core\include\numpy'
LIBS += 'D:\ProgramData\Anaconda3\libs\python3.lib'
LIBS += 'D:\ProgramData\Anaconda3\libs\python3_d.lib'
LIBS += 'D:\ProgramData\Anaconda3\libs\python37.lib'
LIBS += 'D:\ProgramData\Anaconda3\libs\python37_d.lib'
 (If there is no python3_d.lib, python37_d.lib, copy the original files of python3.lib and python37.lib, and add the suffix of ‘_d’ after them)

11、	Click the compile button to test whether the application is output





The problems encountered are as follows:
1、	Line 448 of object.h
 
The reason is that slots in python's object.h conflict with Qt's Slot.
solution:
Original:
typedef struct{
    const char* name;
    int basicsize;
    int itemsize;
    unsigned int flags;
    PyType_Slot *slots; /* terminated by slot==0. */
} PyType_Spec;
Change:
typedef struct{
    const char* name;
    int basicsize;
    int itemsize;
    unsigned int flags;
    #undef slots     // Here to cancel the slots macro definition
    PyType_Slot *slots; /* terminated by slot==0. */
    #define slots Q_SLOTS　　// The restoration of the slots macro definition here is consistent with that in QObjectDefs.h in QT
} PyType_Spec;

2、	he import_array function reports an error
{
import_array();
}
Select the error message and jump to the error location: line 1531 of the _multiarray_api.h function
Remove the “return NULL” of this row;

