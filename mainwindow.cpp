#include "mainwindow.h"
#include "ui_mainwindow.h"


MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    connect(this,SIGNAL(SendRegistrationImage(QImage)),&registrationmodule,SLOT(ReceiveRegistrationImage(QImage)));
    ui->label->setScaledContents(true);
//    Mat image = imread("../1.png");
//    emit SendRegistrationImage(MatToQImage(image));
}

MainWindow::~MainWindow()
{
    delete ui;
}

//初始化
Mat MainWindow::Python_OneFrame(Mat input)
{
    PyObject* PyArray_Frame = Mat2PyArray(input);
    if (PyArray_Frame ==nullptr)
    {
        cout << "no frame" << endl;
    }
    int x = input.size().width;
    int y = input.size().height;

    Fix_Frame = PyObject_CallMethod(pInstance_online, "NCC_framebyframe", "O", PyArray_Frame);
    if (Fix_Frame == NULL) {
        cout << "cannot registrate frame" << endl;
    }

    uchar *data = (uchar *)PyByteArray_AsString(Fix_Frame);
    Mat output_img(y, x, CV_8UC1, data);

    return output_img;
}

PyObject* MainWindow::Mat2PyArray(Mat TestFrame)
{
    Mat img;
    cvtColor(TestFrame, img, CV_BGR2GRAY);
    auto sz = img.size();
    int x = sz.width;
    int y = sz.height;

    //cv::Mat to PyObject
    npy_intp dim[2] = { y,x };
    PyObject* PyArray_online= PyArray_SimpleNewFromData(2, dim, NPY_UBYTE, img.data);

    return PyArray_online;
}

void MainWindow::Python_Preprocess(QString Temp_filepath)
{
    pClass_pre = PyDict_GetItemString(pDict, "Preprocess");//获取目标类
    if (pClass_pre == NULL) {
        cout << "cannot find Preprocess class" << endl;
    }

    pArgs_pre = PyTuple_New(1); //传入参数
    string temp_str = Temp_filepath.toStdString();
//    cout << temp_str << endl;
    const char *ctemp_str = temp_str.c_str();
    //cout << ctemp_str << endl;
    PyTuple_SetItem(pArgs_pre, 0, Py_BuildValue("s", ctemp_str)); //0：表示序号。第一个参数。
    //PyTuple_SetItem(pArgs_pre, 0, Py_BuildValue("s", "E:\\C++pythontest\\msCam22.avi")); //0：表示序号。第一个参数。

    if (pArgs_pre == NULL) {
        cout << "cannot find videopath" << endl;
    }

    pConstruct_pre = PyInstanceMethod_New(pClass_pre);//类的初始化，执行python的类中__init__函数
    if (pConstruct_pre == NULL)
    {
        cout << "cannot find Construct function" << endl;
    }
//    cout<<"Arg:"<<pArgs_pre<<endl;

    pInstance_pre = PyObject_CallObject(pConstruct_pre, pArgs_pre);//生成python实例
    if (pInstance_pre == NULL)
    {
        cout << "cannot find preprocess instance" << endl;
    }
//    cout << pInstance_pre << endl;

    Temp = PyObject_CallMethod(pInstance_pre, "generate_template", NULL);
    if (Temp == NULL) {
        cout << "cannot generate template" << endl;
        return;
    }
    cout << "successful running python function" << endl;

    pClass_online = PyDict_GetItemString(pDict, "NCCProject");//获取目标类
    if (pClass_online == NULL) {
        cout << "cannot find NCCProject class" << endl;
    }

    pArgs_online = PyTuple_New(2); //传入参数
    PyTuple_SetItem(pArgs_online, 0, Temp); //0：表示序号。第一个参数。
    PyTuple_SetItem(pArgs_online, 1, Py_BuildValue("s", ctemp_str)); //1：表示序号。第二个参数。

    if (pArgs_online == NULL) {
        cout << "cannot find arg" << endl;
    }

    pConstruct_online = PyInstanceMethod_New(pClass_online);//类的初始化，执行python的类中__init__函数
    if (pConstruct_online == NULL)
    {
        cout << "cannot find Construct function" << endl;
    }
    cout<<"Arg:"<<pArgs_online<<endl;

    pInstance_online = PyObject_CallObject(pConstruct_online, pArgs_online);//生成python实例
    if (pInstance_online == NULL)
    {
        cout << "cannot find preprocess instance" << endl;
    }
    cout << pInstance_online << endl;

    cout << "GenerateTemp Successfully!" << endl;
}


int MainWindow::addnum(PyObject* pArgs, PyObject* pInstance)
{
    PyObject* result = PyObject_CallMethod(pInstance, "add", NULL);//调用实例中的函数
    if (result == NULL) {
        cout << "cannot  call function" << endl;
        return 0;
    }

    int nResult;
    PyArg_Parse(result, "i", &nResult);//i表示转换成int型变量。在这里，最需要注意的是：PyArg_Parse的最后一个参数，必须加上“&”符号。

    return nResult;
}

//Python环境初始化
void MainWindow::PythonInit()
{
    Py_SetPythonHome(L"C:/ProgramData/Anaconda3");
    Py_Initialize();//PY的初始化放在主函数中，其他函数即可完成py初始化
    cout << "begin python programm" << endl;
    if (PyArray_API == NULL)
    {
        import_array();
    }
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('./')");

    pModule = PyImport_ImportModule("registration");//导入python 脚本
    if (pModule == NULL) {
        cout << "cannot find the python file" << endl;
    }

    pDict = PyModule_GetDict(pModule);//获取脚本中所有的类和函数
    if (pDict == NULL) {
        cout << "cannot find the dictionary" << endl;
    }

    cout << "Python Initialize Successfully!" << endl;
}

QImage MainWindow::MatToQImage(const cv::Mat& mat)
{
    // 8-bits unsigned, NO. OF CHANNELS = 1
    if(mat.type() == CV_8UC1)
    {
        QImage image(mat.cols, mat.rows, QImage::Format_Indexed8);
        // Set the color table (used to translate colour indexes to qRgb values)
        image.setColorCount(256);
        for(int i = 0; i < 256; i++)
        {
            image.setColor(i, qRgb(i, i, i));
        }
        // Copy input Mat
        uchar *pSrc = mat.data;
        for(int row = 0; row < mat.rows; row ++)
        {
            uchar *pDest = image.scanLine(row);
            memcpy(pDest, pSrc, mat.cols);
            pSrc += mat.step;
        }
        return image;
    }
    // 8-bits unsigned, NO. OF CHANNELS = 3
    else if(mat.type() == CV_8UC3)
    {
        // Copy input Mat
        const uchar *pSrc = (const uchar*)mat.data;
        // Create QImage with same dimensions as input Mat
        QImage image(pSrc, mat.cols, mat.rows, mat.step, QImage::Format_RGB888);
        return image.rgbSwapped();
    }
    else if(mat.type() == CV_8UC4)
    {
        qDebug() << "CV_8UC4";
        // Copy input Mat
        const uchar *pSrc = (const uchar*)mat.data;
        // Create QImage with same dimensions as input Mat
        QImage image(pSrc, mat.cols, mat.rows, mat.step, QImage::Format_ARGB32);
        return image.copy();
    }
    else
    {
        qDebug() << "ERROR: Mat could not be converted to QImage.";
        return QImage();
    }
}

void MainWindow::on_pushButton1_clicked()
{
    if (registrationmodule.isHidden())
    {
        cout << "show" << endl;
        registrationmodule.show();
    }
//    if (registrationmodule.isVisible())
//    {
//        cout << "hide" << endl;
//        registrationmodule.hide();
//    }
}

void MainWindow::on_pushButton2_clicked()
{
    cout<< "[System]Motion Correction" << endl;
    Mat TestFrame;//待处理视频帧
    VideoCapture TestVideo;//播放视频
//    TestVideo.open("D:\\msCam1.avi");
    TestVideo.open(Process_filepath.toStdString());
    int fcount = TestVideo.get(CAP_PROP_FRAME_COUNT);//全部帧数
    cout<< "[System] All Frame " << fcount << endl;
    for (int m=1; m<fcount; m++)
    {
        TestVideo >> TestFrame;
        if (TestFrame.empty())
        {
            break;
            qDebug()<<"TestFrame is empty";
        }
        ui->label->setPixmap(QPixmap::fromImage(MatToQImage(TestFrame)));
        Mat OutFrame = Python_OneFrame(TestFrame);
        cout<< "[System] Frame " << m << endl;
        //发送图片给模块
        emit SendRegistrationImage(MatToQImage(OutFrame));
        Sleep(30);
//        namedWindow("output", 1);
//        imshow("output_img",OutFrame);
    }
    cout << "[System]Successful running" << endl;
}

void MainWindow::Sleep(int msec)
{
    QTime dieTime = QTime::currentTime().addMSecs(msec);
    while( QTime::currentTime() < dieTime )
    QCoreApplication::processEvents(QEventLoop::AllEvents, 100);
}

void MainWindow::on_pushButton_clicked()
{
    cout<< "[System]PythonInit" << endl;
    PythonInit();
    cout<< "[System]Preprocess" << endl;
//    Python_Preprocess("D:\\msCam1.avi");

    QString file_path = QFileDialog::getOpenFileName(this,"Open Temp file","../");
    if (file_path.isEmpty() ==false)
    {
        Temp_filepath = file_path;
    }
    Python_Preprocess(Temp_filepath);
}

void MainWindow::on_pushButton3_clicked()
{
    cout<< "[System]Select Process Video" << endl;
    QString file_path = QFileDialog::getOpenFileName(this,"Open Process file","../");
    if (file_path.isEmpty() ==false)
    {
        Process_filepath = file_path;
    }
}
