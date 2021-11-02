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
    loginPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page1_login.ui'))[0]
    aiFreePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page2_aifree.ui'))[0]
    selExercisePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page3_selectexercise.ui'))[0]
    posePage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page4_pose.ui'))[0]
    trainerPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page5_trainer.ui'))[0]
    weightPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page6_weight.ui'))[0]
    exercisingPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page7_exercising.ui'))[0]
    restPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page8_rest.ui'))[0]
    finishPage = uic.loadUiType(os.path.join(os.path.abspath('ui'), 'page9_finish.ui'))[0]
    planPopup = uic.loadUiType(os.path.join(os.path.abspath('ui'), 's_planpopup.ui'))[0]

except FileNotFoundError :
    #kimsungsoo 경로 예외 추가
    loginPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page1_login.ui'))[0]
    aiFreePage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page2_aifree.ui'))[0]
    selExercisePage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page3_selectexercise.ui'))[0]
    posePage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page4_pose.ui'))[0]
    trainerPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page5_trainer.ui'))[0]
    weightPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page6_weight.ui'))[0]
    exercisingPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page7_exercising.ui'))[0]
    restPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page8_rest.ui'))[0]
    finishPage = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 'page9_finish.ui'))[0]
    planPopup = uic.loadUiType(os.path.join(os.path.abspath('python/Virtual-Fit/ui'), 's_planpopup.ui'))[0]

def goNextPage():
    widget.setCurrentIndex(widget.currentIndex()+1)

def goBackPage():
    widget.setCurrentIndex(widget.currentIndex()-1)

def goHomePage(num):
    widget.setCurrentIndex(widget.currentIndex()-int(num))

#1 로그인 페이지
class LoginPage(QDialog, loginPage):
    def __init__(self):
        super(LoginPage, self).__init__()
        self.setupUi(self)

        #self.login_btn.clicked.connect(goNextPage)
        self.pass_btn.clicked.connect(goNextPage)

#2 ai free 선택 페이지
class AiFreePage(QDialog, aiFreePage):
    def __init__(self):
        super(AiFreePage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(goBackPage)
        self.logout_btn.clicked.connect(goBackPage)
        self.ai_btn.clicked.connect(goNextPage)
        #self.free_btn.clicked.connect(goNextPage)

#3 운동자세 선택 페이지
class SelExercisePage(QDialog, selExercisePage):
    def __init__(self):
        super(SelExercisePage, self).__init__()
        self.setupUi(self)

        self.all_btn.clicked.connect(goNextPage)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(2))

#4 자세 피드백 영상 페이지
class PosePage(QDialog, posePage):
    def __init__(self):
        super(PosePage, self).__init__()
        self.setupUi(self)
        
        self.weight_btn.clicked.connect(goNextPage)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(3))

#5 트레이너 설명 페이지 삽입_211102
class TrainerPage(QDialog, trainerPage):
    def __init__(self):
        super(TrainerPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(4))

#6 중량 선택 페이지 순서 수정
class WeightPage(QDialog, weightPage):
    def __init__(self):
        super(WeightPage, self).__init__()
        self.setupUi(self)

        self.setplan_btn.clicked.connect(goNextPage)
        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(5))

#윤성근 무게 설정 버튼 기능 제거_211102 - 다이얼로 변환해야함.

#7 운동중 페이지
class ExercisingPage(QDialog, exercisingPage):
    def __init__(self):
        super(ExercisingPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(6))

#8 휴식 페이지
class RestPage(QDialog, restPage):
    def __init__(self):
        super(RestPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(7))

#9 운동 끝 페이지
class FinishPage(QDialog, finishPage):
    def __init__(self):
        super(FinishPage, self).__init__()
        self.setupUi(self)

        self.back_btn.clicked.connect(goBackPage)
        self.home_btn.clicked.connect(lambda: goHomePage(8))


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
    trainerPage = TrainerPage()
    weightPage = WeightPage()
    exercisingPage = ExercisingPage()
    restpage = RestPage()
    fisishpage = FinishPage()
    planPopup = PlanPopup()

    #widget에 모든 페이지 추가
    widget.addWidget(loginPage)
    widget.addWidget(aiFreePage)
    widget.addWidget(selExercisePage)
    widget.addWidget(posePage)
    widget.addWidget(trainerPage)
    widget.addWidget(weightPage)
    widget.addWidget(exercisingPage)
    widget.addWidget(restpage)
    widget.addWidget(fisishpage)
    widget.addWidget(planPopup)  

    #widget 크기와 보여주는 함수
    widget.setFixedHeight(1920)  # 높이
    widget.setFixedWidth(1080)  # 너비
    widget.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")