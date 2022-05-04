#include "registrationmodule.h"
#include "ui_registrationmodule.h"
#include <QDebug>

RegistrationModule::RegistrationModule(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::RegistrationModule)
{
    ui->setupUi(this);

    ui->label_Registration->setScaledContents(true);
    //设置窗口标题
    setWindowTitle("Registration Display");


}

RegistrationModule::~RegistrationModule()
{
    delete ui;
}

void RegistrationModule::ReceiveRegistrationImage(QImage image)
{
//    qDebug()<<"sss";
    ui->label_Registration->setPixmap(QPixmap::fromImage(image));
}
