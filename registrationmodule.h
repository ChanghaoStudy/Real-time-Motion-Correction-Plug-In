#ifndef REGISTRATIONMODULE_H
#define REGISTRATIONMODULE_H

#include <QWidget>

namespace Ui {
class RegistrationModule;
}

class RegistrationModule : public QWidget
{
    Q_OBJECT

public:
    explicit RegistrationModule(QWidget *parent = nullptr);
    ~RegistrationModule();

private:
    Ui::RegistrationModule *ui;

private slots:
    void ReceiveRegistrationImage(QImage image);
};

#endif // REGISTRATIONMODULE_H
