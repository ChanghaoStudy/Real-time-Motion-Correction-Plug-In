QT       += core gui
QT       += charts


greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++11

# The following define makes your compiler emit warnings if you use
# any Qt feature that has been marked deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

TARGET = MiniScopeControl  #应用程序名
TEMPLATE = app  #生成的makefile的模板类型

SOURCES += \
    main.cpp \
    mainwindow.cpp \
    registrationmodule.cpp

HEADERS += \
    mainwindow.h \
    registrationmodule.h

FORMS += \
    mainwindow.ui \
    registrationmodule.ui

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

#Environment opencv3.43_mingw_64
INCLUDEPATH += C:\opencv3.43_mingw_64\install\include
LIBS += -L C:\opencv3.43_mingw_64\install\x64\mingw\lib\libopencv_*.a \

# python enviroment
INCLUDEPATH += 'C:\ProgramData\Anaconda3\include'
INCLUDEPATH += 'C:\ProgramData\Anaconda3\Lib\site-packages\numpy\core\include\numpy'
LIBS += 'C:\ProgramData\Anaconda3\libs\python3.lib'
LIBS += 'C:\ProgramData\Anaconda3\libs\python3_d.lib'
LIBS += 'C:\ProgramData\Anaconda3\libs\python37.lib'
LIBS += 'C:\ProgramData\Anaconda3\libs\python37_d.lib'
