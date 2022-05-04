#ifndef MAINWINDOW_H
#define MAINWINDOW_H
#include <Python.h>
#include <QMainWindow>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include "registrationmodule.h"

#include <QDebug>
#include <QTime>
#include <QFileDialog>

#include <arrayobject.h>
#include <QCoreApplication>
#include <QDebug>
#include <iostream>
using namespace std;
using namespace cv;

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

    //python para
    PyObject* pModule = nullptr;
    PyObject* pDict = nullptr;
    PyObject* pClass_pre = nullptr;
    PyObject* pArgs_pre = nullptr;
    PyObject* pConstruct_pre = nullptr;
    PyObject* pInstance_pre = nullptr;
    PyObject* Temp = nullptr;
    int addnum(PyObject* pArgs, PyObject* pInstance);
    QString Temp_filepath;
    QString Process_filepath;
    PyObject* pClass_online = nullptr;
    PyObject* pArgs_online = nullptr;
    PyObject* pConstruct_online = nullptr;
    PyObject* pInstance_online = nullptr;
    PyObject* Fix_Frame = nullptr;

    void PythonInit();
    void Python_Preprocess(QString);
    Mat Python_OneFrame(Mat input);
    PyObject* Mat2PyArray(Mat TestFrame);
    QImage MatToQImage(const cv::Mat& mat); 

    void Sleep(int msec);

private slots:
    void on_pushButton1_clicked();
    void on_pushButton2_clicked();

    void on_pushButton_clicked();

    void on_pushButton3_clicked();

signals:
    void SendRegistrationImage(QImage image);

private:
    Ui::MainWindow *ui;

    RegistrationModule registrationmodule;
};
#endif // MAINWINDOW_H
