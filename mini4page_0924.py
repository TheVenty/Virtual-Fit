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

try :
    #임포트 완료 - ui연결
    loginPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_loginpage_1.ui'))[0]
    aiFreePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_aifreepage.ui'))[0]
    selExercisePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_slectexercisepage.ui'))[0]
    posePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_posepage.ui'))[0]
    weightPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_weightpage.ui'))[0]
    planPopup = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_planpopup.ui'))[0]

except FileNotFoundError :
    #kimsungsoo 경로 예외 추가
    loginPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 's_loginpage_1.ui'))[0]
    aiFreePage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 's_aifreepage.ui'))[0]
    selExercisePage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 's_slectexercisepage.ui'))[0]
    posePage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 's_posepage.ui'))[0]
    weightPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 's_weightpage.ui'))[0]
    planPopup = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 's_planpopup.ui'))[0]


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

        #self.login_btn.clicked.connect(goNextPage)
        self.pass_btn.clicked.connect(goNextPage)

class AiFreePage(QDialog, aiFreePage):
    def __init__(self):
        super(AiFreePage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(goBackPage)
        self.logout_btn.clicked.connect(goBackPage)
        #self.ai_btn.clicked.connect(goNextPage)
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

#윤성근 중량 선택 페이지 삽입_211013
class WeightPage(QDialog, weightPage):
    def __init__(self):
        super(WeightPage, self).__init__()
        self.setupUi(self)

        self.setplan_btn.clicked.connect(goNextPage)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(4))

#윤성근 무게 설정 버튼 기능 삽입_211015
        self.kg10_btn.clicked.connect(kg10Method)
        self.kg50_btn.clicked.connect(kg50Method)
        self.kg100_btn.clicked.connect(kg100Method)
        self.kg200_btn.clicked.connect(kg200Method)
        self.kg400_btn.clicked.connect(kg400Method)


def kg10Method(self) : 
    kg10 = 10
    kgValue = kg10

    print(kgValue)

def kg50Method(self) : 
    kgValue = kgValue + 50

    print(kgValue)

def kg100Method(self) : 
    kgValue = kgValue + 100

    print(kgValue)

def kg200Method(self) : 
    kgValue = kgValue + 200

    print(kgValue)
        
def kg400Method(self) :
    kgValue = kgValue + 400 

    print(kgValue)


#윤성근 운동 Plan Pop Up 창 삽입_211014 - resetPlan 버튼 누를 시 꺼짐 현상. 원인 모르겠음.
class PlanPopup(QDialog, planPopup):
    def __init__(self):
        super(PlanPopup, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.reset_btn.clicked.connect(self.resetPlan)

        #슬라이드 바의 시그널 사용
        self.set_bar.valueChanged.connect(self.showSetValue)
        self.rep_bar.valueChanged.connect(self.showRepValue)

    #슬라이드 바의 시그널 이용 - 슬라이드 바의 값이 변경되면 해당 라벨에 값을 표시    
    def showSetValue(self) :
     self.set_lb.setText(str(self.set_bar.value()))

    def showRepValue(self) :
        self.rep_lb.setText(str(self.rep_bar.value()))

    def resetPlan(self):
        self.set_lb.setValue(4)
        self.rep_lb.setValue(12)



#이하 main 코드
if __name__ == '__main__':
    # Some setup for qt
    app = QApplication(sys.argv)

    #QstackedWidget 기능 연결 및 인스턴스 생성
    widget = QtWidgets.QStackedWidget()
    loginPage = LoginPage()
    aiFreePage = AiFreePage()
    selExercisePage = SelExercisePage()
    posePage = PosePage()
    weightPage = WeightPage()
    planPopup = PlanPopup()

    #widget에 모든 페이지 추가
    widget.addWidget(loginPage)
    widget.addWidget(aiFreePage)
    widget.addWidget(selExercisePage)
    widget.addWidget(posePage)
    widget.addWidget(weightPage)
    widget.addWidget(planPopup)

    #widget 크기와 보여주는 함수
    widget.setFixedHeight(830)
    widget.setFixedWidth(467)
    widget.show()


    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")