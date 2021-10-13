import sys
import os
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication
import logging.handlers

#로그 생성
logger = logging.getLogger()
fileMaxByte = 1024 * 1024 * 10
formatter = logging.Formatter("%(asctime)s;[%(levelname)s];%(message)s", "%Y-%m-%d %H:%M:%S")
fileHandler = logging.handlers.RotatingFileHandler('./virtual_Fit.log', maxBytes=fileMaxByte, backupCount=5)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

#임포트 완료 - ui연결
loginPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_loginpage_1.ui'))[0]
aiFreePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_aifreepage.ui'))[0]
selExercisePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_slectexercisepage.ui'))[0]
posePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_posepage.ui'))[0]
weightPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_weightpage.ui'))[0]


def goNextPage():
    widget.setCurrentIndex(widget.currentIndex()+1)

def goBackPage():
    widget.setCurrentIndex(widget.currentIndex()-1)

def goHomePage(num):
    widget.setCurrentIndex(widget.currentIndex()-int(num))

class LoginPage(QDialog, loginPage):
    def __init__(self):
        super(LoginPage, self).__init__()
        self.setupUi(self)

        self.login_btn.clicked.connect(goNextPage)
        self.pass_btn.clicked.connect(goNextPage)

class AiFreePage(QDialog, aiFreePage):
    def __init__(self):
        super(AiFreePage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(goBackPage)
        self.logout_btn.clicked.connect(goBackPage)
        self.ai_btn.clicked.connect(goNextPage)
        self.free_btn.clicked.connect(goNextPage)

class SelExercisePage(QDialog, selExercisePage):
    def __init__(self):
        super(SelExercisePage, self).__init__()
        self.setupUi(self)

        self.all_btn.clicked.connect(goNextPage)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(2))


class PosePage(QDialog, posePage):
    def __init__(self):
        super(PosePage, self).__init__()
        self.setupUi(self)

        self.weight_btn.clicked.connect(goNextPage)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(3))

#중량 선택 페이지 삽입_211013
class WeightPage(QDialog, weightPage):
    def __init__(self):
        super(WeightPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(4))


#이하 main 코드
if __name__ == '__main__':
    # Some setup for qt
    app = QApplication(sys.argv)

    #QstackedWidget 기능 연결 및 인스턴스 생성
    widget = QtWidgets.QStackedWidget()
    s_loginPage = LoginPage()
    s_aiFreePage = AiFreePage()
    s_selExercisePage = SelExercisePage()
    s_posePage = PosePage()
    s_weightPage = WeightPage()


    #widget에 모든 페이지 추가
    widget.addWidget(s_loginPage)
    widget.addWidget(s_aiFreePage)
    widget.addWidget(s_selExercisePage)
    widget.addWidget(s_posePage)
    widget.addWidget(s_weightPage)

    #widget 크기와 보여주는 함수
    widget.setFixedHeight(830)
    widget.setFixedWidth(467)
    widget.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")