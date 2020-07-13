import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PIL import Image

import ctypes
import cv2
import datetime
import os

from time import sleep

import numpy

form_class = uic.loadUiType("mosaic6.ui")[0]


###############변경 대비 업데이트 내용 (preparation for change)##################
# 기연 - (1) 사이즈 줄인 후 모자이크
# 예솔 - (1) 라벨에 이미지 띄우기 여부 (2)모자이크 대체 이미지  - 스펀지밥
# 혜나 - (1) 사용자가 파일 이름 선택
# 소영 - (1) 좌표 여러개 선택 (2)모자이크 선택 (3)어떤게 모자이크
# 희주 - (1) 에러 메세지 저장 (2) 중앙 제외 모자이크
##################################################################################


class MyWindow(QMainWindow, form_class):
    ############################### 예솔(1) - 라벨에 이미지 띄우기 여부 #########################
    # false : 원래 프로그램
    # True : 모자이크할 곳 없는 사진은 안뜸
    # <preparation for change>
    ys_flag = False;
    # </preparation for change>
    ############################### 예솔(2) - 모자이크 대체 이미지(스펀지밥) #########################
    # false : 원래 프로그램
    # True : 모자이크할 곳 없는 사진은 안뜸
    # <preparation for change>
    ys_rp_flag = False;
    rp_img = cv2.imread('spongebob.jpg', cv2.IMREAD_COLOR)
    # </preparation for change>

    ############################### 소영(1) - 좌표 여러개 선택 #########################
    # false : 한 개 선택 # True : 여러개 선택
    # <preparation for change>
    '''
    <2번째 요구사항으로 인한 변경>
            기존에 대비로 만들어 둔 multi_flag = False로 좌표 여러개 선택 기능을 사용하지 않다가
            이번 요구사항 중 사각형, 점 좌표가 여러개 선택 가능하게 해달라는 요구가 있어
            multi_flag = True로 변경하였다.=>이건 진짜 True로만 바꿔서 사용 가능했다!!!!!
    '''
    multi_flag = True
    # </preparation for change>

    ############################### 소영(2) - 모자이크 될 영역만 선택 #########################
    # false : 모자이크 영역 선택 안함 # True : 모자이크 영역 선택함
    # <preparation for change>
    '''
    <2번째 요구사항으로 인한 변경>
        대비로 만들어둔 모자이크 될 영역 선택 기능 사용하면서 변수에 변화가 생김.
        기존 대비는 모자이크 영역 선택과 제외 영역 선택을 동시에 할 수 있게 해놓았으나
        이번 요구에서는 둘 중 하나의 기능만 사용하게 해서 대비로 만든 3개의 flag가 아니라 mosaic_mode_flag만 남김.

            (기존)
            -mosaic_mode_flag : 모자이크 기능을 사용할건인지에 관한 flag
            -mosaic_sel_flag : 모자이크 영역 선택 버튼이 눌렸는지 나타내는 flag.
            -getcoor_flag : 기존엔 모자이크의 좌표 선택과 좌표 제외의 좌표 선택이 input_label에 동시에 나타날 수 있었는데,
            이를 나타내 input_label에 적절한 이벤트가 표시될 수 있도록 한 flag

            (변경)
            -mosaic_mode_flag : 라디오 버튼에서 모자이크 영역 선택/ 제외 영역 선택 기능 중 어떤게
            선택되었는지를 나타내는 flag
            -mosaic_sel_flag : mosaic_mode_flag가 기능 대신해서 사라짐
            -getcoor_flag : input_label에는 모자이크/제외 중 하나만 발생하므로 사라짐

        mosaic_mode_flag 선언은 아래 2번째 요구사항으로 인해 추가된 변수들이 모여있는 146번째 줄에 있음.
    </>

    <기존 코드>
        mosaic_mode_flag = True
        #mosaic_sel_flag = False
        #getcoor_flag = False  # false면 좌표 선택이 클릭된거고 true면 모자이크 영역이 선택된거임
    </기존 코드>
    '''
    ##아래는 모자이크 될 영역만 선택하기 위해 필요한 변수
    #mosaic_sel_flag = False
    #getcoor_flag = False  # false면 좌표 선택이 클릭된거고 true면 모자이크 영역이 선택된거임
    mosaic_x = []
    mosaic_y = []
    mosaic_origin_x = []
    mosaic_origin_y = []
    # </preparation for change>


    ############################### 소영(3) - 어떤 것이 모자이크 될 것인가?? #########################
    # mosaic_things 1:얼굴, 2: 왼쪽 눈, 3:오른쪽 눈, 4:스마일, 5:상반신
    # <preparation for change>
    # cascade_file = "C:/Users/soyoung/AppData/Local/Programs/Python/Python36-32/Lib/site-packages/cv2/data/haarcascade_frontalface_alt.xml"
    cascade_file = ""
    mosaic_things = 1
    # </preparation for change>

    ############################### 희주 - 에러메세지 로그 출력 #########################
    # <preparation for change>
    errsaveFlag = False
    errLog = ""
    # </preparation for change>

    ############################### 혜나 - 파일을 다른 이름으로 저장 #########################
    # 파일을 다른이름으로 저장 할 시
    # <preparation for change>
    hn_flag = False
    # </preparation for change>

    ############################### 희주 - 주인공 제외 나머지 모자이크 #########################
    # <preparation for change>
    '''
    주인공 제외 나머지 모자이크 기능과 유사하게 어떤 점에서 가장 가까운 얼굴 제외/모자이크 기능과
     이에 따른 ui의 변경이 요구되었다.
    - 주인공 제외 나머지 모자이크 기능을 사용하는지를 나타내는 hero_mode_flag는
    점과 중앙에 이 기능이 쓰이면서 flag를 둘 필요 없어짐
    - 주인공 제외 나머지 모자이크 버튼이 클릭되는지 나타내는 hero_flag는 사각/중앙/점과 같은
     선택 방법(변수 option_method(148번째 줄)가 선택 방법을 나타낸다)에 편입되어 사라짐.

    <기존 코드>
        #hero_mode_flag = True  # 주인공 제외 나머지 모자이크 기능을 사용할 것인가?
        #hero_flag = False  # 해당 버튼이 클릭되었는가?
    </기존 코드>
    '''
    # </preparation for change>

    ################################케스케이드 파일, 파일 탐색창 루트 경루 ####################################
    root_path = "C:/Users/soyoung/AppData/Local/Programs/Python/Python36-32/Lib/site-packages/cv2/data/"
    file_root_path = "C:/Users/soyoung/Desktop"
    #################

    ### 181110 기연 추가 ###
    # <preparation for change>
    #over_size 기능 사용 : True, 기능 사용 x : False
    over_size_flag = False
    over_size = 0  # 사이즈 초과여부 flag (0: 초과 X / 1: 초과 O)
    # </preparation for change>
    ##########################

    '''2번째 요구사항때문에 추가된 멤버 변수!!!!!!!!!!!'''
    ###########2번째 요구 사항 ##############

    mosaic_mode_flag = False  #모자이크/제외 라디오 버튼 True : 모자이크 영역 선택/ False : 좌표 제외
    option_method = 1 #좌표 선택 방법 라디오 버튼 0 : 사각/ 1:중앙 / 2:점
    pnum = 1 #콤보박스 얼굴 수(0~10 선택 가능)

    input_label_width = 0 #라벨 기준으로 계산하다보니 input_label의 width와 height가 계속 쓰여서 이번에 추가했슴다.
    input_label_height = 0

    ##############################3

    file_path = ""
    file_paths = []
    selFlag = False  # 좌표 선택이 클릭되었는가?
    coordFlag = False  # 좌표가 정상 선택 되었는가?(True : 0개, 2개 선택시 / False : 그 외 )
    flag = False  # 이미지 라벨에 이미지가 그려져야 하는가?
    dirName = ""  # 새로운 디렉토리 생성

    x = []  # 선택 좌표를 담을 list
    y = []
    original_x = []
    original_y = []

    # 여러개를 한번에 검사하다보니 추가된 변수
    checkError = True  # 이미지가 에러를 통과했는지 확인한다.
    errorResult = []

    ErrorMsg = ""

    width = 0;
    height = 0;  # 이미지의 너비와 높이

    # 초기화 함수
    def __init__(self):
        super().__init__();
        super().setupUi(self);

        ############################### 소영(3) - 무엇이 모자이크 될 것인가? #########################
        # <preparation for change>
        self.whatMosaic(self.mosaic_things)
        # </preparation for change>
        '''
        <2번째 요구사항으로 인한 변경>
            라디오 버튼 5개와 콤보 박스 한 개가 추가되면서 버튼이 무지 많아짐. 더 이상 번호를 붙여 쓸 수 없어
            버튼의 고유 이름을 정해주게 되었습니다...
            btn1->btn_sel_img (이미지 선택)
            btn2->btn_convers (변환)
            btn3->btn_sel_pos (좌표 선택)
            btn4->btn_help (도움말)
            btn5->btn_exit (종료)
            btn6->btn_mosaic_area (모자이크 영역 선택->라디오 버튼 '모자이크 영역 선택'으로 수정)
            btn7->btn_cent (주인공 제외 모자이크 -> 라디오 버튼 '중앙'으로 수정)

            -추가된 버튼
            btn_except_area (제외영역 선택 라디오 버튼)
            btn_rect (사각형 라디오 버튼)
            btn_point (점 라디오 버튼)
            btn_pnum (사람 수 콤보 박스)

            <기존 코드>
                self.btn1.clicked.connect(self.btn1_clicked)  # 이미지 선택
                self.btn2.clicked.connect(self.btn2_clicked)  # 변환
                self.btn3.clicked.connect(self.btn3_clicked)  # 좌표 선택
                self.btn4.clicked.connect(self.btn4_clicked)  # 도움말
                self.btn5.clicked.connect(self.btn5_clicked)  # 종료
                # self.btn5.clicked.connect(self.closeEvent())
                ############################### 소영(2) - 모자이크 될 영역만 선택 #########################
                # <preparation for change>
                self.btn6.clicked.connect(self.btn6_clicked)  # 모자이크 영역 선택
                if (self.mosaic_mode_flag):
                    self.btn6.show()
                else:
                    self.btn6.hide()
                # </preparation for change>
                ############################### 희주 - 주인공 제외 나머지 모자이크 #########################
                # <preparation for change>
                self.btn7.clicked.connect(self.btn7_clicked)  # 모자이크 영역 선택
                if (self.hero_mode_flag):
                    self.btn7.show()
                else:
                    self.btn7.hide()
            # </preparation for change>
        '''
        ###########################2번째 요구사항 ##############################################3
        self.btn_sel_img.clicked.connect(self.btn_sel_img_clicked)  # 이미지 선택
        self.btn_help.clicked.connect(self.btn_help_clicked)  # 도움말
        self.btn_exit.clicked.connect(self.btn_exit_clicked)  # 종료

            #좌표 제외/ 모자이크 영역 선택 라디오 그룹
        self.btn_except_area.clicked.connect(self.ModeRadioGroupClicked)
        self.btn_mosaic_area.clicked.connect(self.ModeRadioGroupClicked)
            #좌표 선택 방법 : 사각/중앙/점
        self.btn_rect.clicked.connect(self.SelRadioGroupClicked)
        self.btn_cent.clicked.connect(self.SelRadioGroupClicked)
        self.btn_point.clicked.connect(self.SelRadioGroupClicked)
            #사람 인원 수 콤보 박스 선택
        self.btn_pnum.currentTextChanged.connect(self.PnumComboClicked)

        self.btn_convers.clicked.connect(self.btn_convers_clicked)  # 변환
        self.btn_sel_pos.clicked.connect(self.btn_sel_pos_clicked)  # 좌표 선택

        self.input_label_width = self.input_label.width()
        self.input_label_height = self.input_label.height()

        ######################################################3



        # 제출, 좌표 선택 버튼 초기 비활성화 상태
        self.buttonActive(False, self.btn_convers, False, self.btn_sel_pos)
        #self.buttonActive(False, self.btn_mosaic_area, False, self.btn_cent)
        self.input_label.mousePressEvent = self.getPixel  # input_label을 클릭할때 getpixel이벤트 발생

        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    def whatMosaic(self, idx):

        self.cascade_file = self.root_path

        if (idx == 1):
            self.cascade_file += "haarcascade_frontalface_alt.xml"
        elif (idx == 2):
            self.cascade_file += "haarcascade_lefteye_2splits.xml"
        elif (idx == 3):
            self.cascade_file += "haarcascade_righteye_2splits.xml"
        elif (idx == 4):
            self.cascade_file += "haarcascade_smile.xml"
        elif (idx == 5):
            self.cascade_file += "haarcascade_upperbody.xml"
        else:
            self.cascade_file += "haarcascade_frontalface_alt.xml"

    def errOutput(self, err_num=0, idx=0):
        if (err_num == 1):  # 파일 용량 제한 초과
            f_split = self.file_paths[idx].split('/')
            self.ErrorMsg = self.ErrorMsg + f_split[len(f_split) - 1] + " 파일 용량 제한 초과.\n"
            # Error_msg = f_split[len(f_split)-1]+" 파일 용량 제한 초과."
            # msg = ctypes.windll.user32.MessageBoxW(None, Error_msg, "오류 메세지", 0)
        elif (err_num == 2):  # 파일 사이즈 초과
            f_split = self.file_paths[idx].split('/')
            self.ErrorMsg = self.ErrorMsg + f_split[len(f_split) - 1] + " 파일 사이즈 제한 범위 초과.\n"
            # Error_msg = f_split[len(f_split)-1]+" 파일 사이즈가 작거나 초과."
            # msg = ctypes.windll.user32.MessageBoxW(None, Error_msg, "오류 메세지", 0)
        elif (err_num == 3):  # 확장자 오류
            f_split = self.file_paths[idx].split('/')
            self.ErrorMsg = self.ErrorMsg + f_split[len(f_split) - 1] + " 표준 확장자가 아닙니다.\n"
            # Error_msg = f_split[len(f_split)-1]+" 표준 확장자가 아닙니다."
            # msg = ctypes.windll.user32.MessageBoxW(None, Error_msg, "오류 메세지", 0)
        elif (err_num == 4):  # 출력오류
            f_split = self.file_path.split('/')
            self.ErrorMsg = self.ErrorMsg + f_split[len(f_split) - 1] + " 이미지 내 얼굴이 없습니다.\n"
            # msg = ctypes.windll.user32.MessageBoxW(None, "이미지 내 얼굴이 없습니다.", "오류 메세지", 0)
        elif (err_num == 5):  # 좌표 중복 오류
            msg = ctypes.windll.user32.MessageBoxW(None, "이미 선택된 좌표가 있습니다. x좌표들 {0}, y좌표들 {1}".format(self.x, self.y),"오류 메세지", 0)
        else:
            msg = ctypes.windll.user32.MessageBoxW(None, "플랫폼 오류입니다.", "오류 메세지", 0)
            # quit()

            # 버튼 활성화 비활성화
            # 변환 버튼 활성화 함수

    def buttonActive(self, active_flag1, btn_sel_img, active_flag2=False, btn_convers=None):
        if btn_convers is None:
            if (type(active_flag1) is bool):
                btn_sel_img.setEnabled(active_flag1)
        else:
            if (type(active_flag1) is bool):
                btn_sel_img.setEnabled(active_flag1)
            if (type(active_flag2) is bool):
                btn_convers.setEnabled(active_flag2)

                # 1.이미지 입력 예외처리
                # 1-1. 파일 사이즈 검사

    def checkVolume(self, idx):
        file_size = os.path.getsize(self.file_paths[idx])

        # KB 로 변환
        file_size = file_size / 1024
        print("파일 용량 : ", file_size, "KB")

        # 파일 용량 제한 초과 (10MB == 10485760B)
        if file_size > 10485760:
            # print('파일 용량 제한 초과')
            print('{0}의 파일 사이즈는 기준 초과.'.format(self.file_paths[idx]))
            self.checkError = False
            self.errOutput(1, idx)
            # quit()
        else:
            self.checkSize(idx)  # 확장자, 용량 검사를 통과해야 가로 세로 크기 검사를 한다.
            # print(self.checkError)
            # 1-2. 파일 크기 검사

    def checkSize(self, idx):
        im = Image.open(self.file_paths[idx])
        file_length = im.size
        print("(가로,세로):", file_length)
        (self.width, self.height) = file_length
        # 파일 사이즈 제한 초과
        if self.width < 75 or self.height < 75:
            # print('파일 사이즈 제한 초과')
            print('{0}의 파일 사이즈는 기준 미만.'.format(self.file_paths[idx]))
            self.checkError = False
            self.errOutput(2, idx)
            # quit()
        if self.width > 5000 or self.height > 5000:
            # print('파일 사이즈 제한 초과')
            print('{0}의 파일 사이즈는 기준 초과.'.format(self.file_paths[idx]))
            #### 181110 에러로 판단 안함 + 리사이즈
            # self.checkError = False
            #self.over_size = 1  # 사이즈 초과함
            ####################################3
            #self.checkError = False
            #self.errOutput(2, idx)

            if(self.over_size_flag):
                self.over_size = 1  # 사이즈 초과함
            else:
                self.checkError = False
            self.errOutput(2, idx)
            # quit()
            # print(self.checkError)
            # 1-3. 파일 확장자 검사

    def checkExtention(self, idx):
        split_str = self.file_paths[idx].split('.')
        split_str_length = len(split_str)
        exe_name = split_str[split_str_length - 1]

        ######### 기연추가부분 (181110) #########
        extention_list = ['jpg', 'jpeg', 'png']  # 가능한 확장자 리스트
        extention_check = 0  # 가능한 확장자인지 판단 flag
        for correct_extention in extention_list:
            if exe_name == correct_extention:  # 옳은확장자
                extention_check = 1
            else:  # 옳지않은 확장자
                pass

        if extention_check == 1:
            print('{0}의 확장자는 {1}로 옳은 확장자이다.'.format(self.file_paths[idx], exe_name))
            # self.checkVolume(idx)#최소한 이미지여야 불러서 가로 세로 검사를 할 수 있슴다.
            self.checkVolume(idx)  # 최소한 이미지여야 용량 검사를 수행합니다.
        else:
            # print("표준 확장자가 아닙니다. 지금 확장자 :"+exe_name)
            self.checkError = False
            print('{0}의 확장자는 {1}로 옳은 확장자가 아니다.'.format(self.file_paths[idx], exe_name))
            self.errOutput(3, idx)

            # 구 코드백업
            # if exe_name == 'jpg' or (exe_name == 'jpeg' or exe_name == 'png'):
            #     print('{0}의 확장자는 {1}로 옳은 확장자이다.'.format(self.file_paths[idx], exe_name))
            #     # self.checkVolume(idx)#최소한 이미지여야 불러서 가로 세로 검사를 할 수 있슴다.
            #     self.checkVolume(idx)  # 최소한 이미지여야 용량 검사를 수행합니다.
            # else:
            #     # print("표준 확장자가 아닙니다. 지금 확장자 :"+exe_name)
            #     self.checkError = False
            #     print('{0}의 확장자는 {1}로 옳은 확장자가 아니다.'.format(self.file_paths[idx], exe_name))
            #     self.errOutput(3, idx)

    def make_dir(self):
        # 파일생성
        now = datetime.datetime.now()
        nowDate = now.strftime('%Y-%m-%d %H-%M-%S')
        # nowDate = now.strftime('%Y-%m-%d')
        self.dirName = nowDate
        changeName = ''
        i = 1;
        while os.path.exists(self.dirName) == True:
            changeName = self.dirName + '(' + str(i) + ')'
            i = i + 1
            if os.path.exists(changeName) == False:
                break
        if i > 1:
            os.mkdir(changeName)
            self.dirName = changeName
        else:
            os.mkdir(self.dirName)

    # 2. 이미지 선택
    def btn_sel_img_clicked(self):

        # 플래그와  선택된 좌표 초기화
        self.flag = False
        # self.selFlag = False
        # self.imgFlag = False
        #self.coordFlag = False

        ############################### 소영(2) - 모자이크 될 영역만 선택 #########################
        # <preparation for change>
        if (len(self.x) > 0):
            self.selFlag = False
            self.x = []
            self.y = []
            self.original_x = []
            self.original_y = []

        '''
        <2번째 요구사항으로 인한 변경>
            모자이크 영역 선택과 제외 영역 선택 이벤트가 동시에 일어나지 않아서
            모자이크 영역 선택과 제외 영역 선택한 좌표 모두 멤버변수 x, y, original_x, original_y를 사용합니다.

            <기존 코드>
                 if (len(self.mosaic_x) > 0):
                    self.mosaic_sel_flag = False
                    self.mosaic_x = []
                    self.mosaic_y = []
                    self.mosaic_origin_x = []
                    self.mosaic_origin_y = []
        # </preparation for change>
        '''

        # 파일생성
        fname = QFileDialog.getOpenFileNames(self, "Open File", self.file_root_path, "Images (*.png *.jpeg *.jpg)");
        self.file_paths, _ = fname
        file_num = len(self.file_paths)

        if (file_num < 1):
            print("선택된 파일이 없습니다.")
            QMessageBox.warning(self, "파일 선택 에러", "선택된 파일이 없습니다.", QMessageBox.Yes)
        else:
            self.file_path = self.file_paths[0]
            self.errorResult = []  # 초기화
            for i in range(file_num):
                self.checkError = True
                self.checkExtention(i)  # checkExtention->checkSize->checkVolume 순으로 검사.
                # self.checkSize(i)
                # self.checkVolume(i)

                if (self.checkError == False):
                    self.errorResult.append(i)

            if (len(self.errorResult) > 0):
                for j in range(len(self.errorResult), 0, -1):
                    del self.file_paths[self.errorResult[j - 1]]  # 입력 조건을 만족하지 못한 사진은 삭제한다.
                QMessageBox.warning(self, "입력 에러 발생", self.ErrorMsg, QMessageBox.Yes)
                ############################### 희주 - 에러메세지 로그 출력 #########################
                # <preparation for change>
                if (self.errsaveFlag == True):
                    self.errLog = "---------<입력 에러>--------\n"
                    self.errLog = self.errLog + (self.ErrorMsg + '\n')
                # </preparation for change>
                self.ErrorMsg = ""

                '''
                <2번째 요구사항으로 인한 변경>
                    이제 여러 장 입력, 한 장 입력 모두 좌표 선택 기능을 사용하기 때문에 버튼 활성화되어야 하는게
                    같음. 그래서 경우를 나누지 않고 변환 버튼만 활성화.
                </>
                '''

            #if (file_num == 1 and len(self.errorResult) == 0):  # 한 개만 선택되면 좌표선택 활성화
               # self.buttonActive(True, self.btn_convers, True, self.btn_sel_pos)
                #self.buttonActive(self.mosaic_mode_flag, self.btn_mosaic_area, self.hero_mode_flag, self.btn_cent)
                #self.flag = True
            #elif (len(self.file_paths) > 0):  # del때문에 파일 개수 달라짐
                #self.buttonActive(True, self.btn_convers, False, self.btn_sel_pos)  # 변환 버튼만 활성화
                #self.buttonActive(False, self.btn_mosaic_area, self.hero_mode_flag, self.btn_cent)

            ###이제 여러개 선택인 경우도 첫번째 파일은 보여준다.
            if (len(self.file_paths) > 0):  # del때문에 파일 개수 달라짐
                self.file_path = self.file_paths[0]
                self.flag = True
                #self.selFlag = True
                self.buttonActive(True, self.btn_convers)
                if self.option_method is not 1:
                    self.buttonActive(True, self.btn_sel_pos)

    # 그리기 이벤트
    def paintEvent(self, event):
        # 선그리기6
        if self.flag:
            w1 = self.input_label_width  # 원본이미지 그리기. 모자이크 이미지는 findFace에서 그려짐
            h1 = self.input_label_height
            self.pixmap = QPixmap(self.file_path).scaled(w1, h1)

            qp = QPainter(self.pixmap)
            qp.drawPixmap(self.pixmap.rect(), self.pixmap)

            '''
            <2번째 요구사항으로 인한 변경>
                모자이크 영역 선택과 제외 영역 선택 이벤트가 동시에 일어나지 않아서
                모자이크 영역 선택과 제외 영역 선택한 좌표 모두 멤버변수 x, y, original_x, original_y를 사용합니다.
                그래서 라벨에 그려줄 때에도 모자이크/제외 둘 중 어떤 모드인지 보고 색만 달리해서
                멤버변수 x, y를 이용해 그려주면 됩니다.

                <기존 코드>
                    if (len(self.mosaic_x) == 2):
                        drawX = min(self.mosaic_x)
                        drawY = min(self.mosaic_y)
                        drawW = abs(self.mosaic_x[0] - self.mosaic_x[1])
                        drawH = abs(self.mosaic_y[0] - self.mosaic_y[1])
                        qp.setPen(Qt.red)
                        qp.drawRect(drawX, drawY, drawW, drawH)
                </코드>


            <2번째 요구사항으로 인한 변경>
                -기존코드는 사각형에 점 2개씩 가져와 그리는 코드입니다.
                -변경된 코드는 option_method(0:사각, 1: 중앙, 2:점) 값이 0이면 사각, 2이면 점이 그려집니다.
                 사각인 경우, 멤버변수 x와 y에서 좌표를 2개씩 가져와 사각형을 그립니다.
                 이 때 색은 mosaic_mode_flag에 따라 좌표 제외면 파란색, 모자이크 영역이면 빨간색으로 그려집니다.
                 점인 경우, 멤버 변수 x와 y에서 좌표를 1개씩 가져와 원을 그립니다.
                 이 때 색은 mosaic_mode_flag에 따라 좌표 제외면 파란색, 모자이크 영역이면 빨간색으로 그려집니다.

                <기존 코드>
                    idx = int(len(self.x) / 2)

                        for i in range(idx):
                            drawX = min(self.x[i * 2], self.x[i * 2 + 1])
                            drawY = min(self.y[i * 2], self.y[i * 2 + 1])
                            drawW = abs(self.x[i * 2] - self.x[i * 2 + 1])
                            drawH = abs(self.y[i * 2] - self.y[i * 2 + 1])
                            qp.setPen(Qt.blue)
                            qp.drawRect(drawX, drawY, drawW, drawH)

            '''
            # idx = 1  # 기본은 좌표 선택 하나임

            # if (self.multi_flag == True):  # 좌표 선택 여러개 할 수 있는 경우

         #   if(self.mosaic_mode_flag):
         #       qp.setPen(Qt.red)
         #   else:
         #       qp.setPen(Qt.blue)

            ##########################<2번째 요구> ########################################
            # 사각형 선택인 경우
            if self.option_method == 0:
                # 모자이크/제외 모드
                if self.mosaic_mode_flag:
                    qp.setPen(Qt.red)#모자이크면 빨강
                else:
                    qp.setPen(Qt.blue)#제외면 파랑
                idx = int(len(self.x) / 2)
                for i in range(idx):
                    drawX = min(self.x[i * 2], self.x[i * 2 + 1])
                    drawY = min(self.y[i * 2], self.y[i * 2 + 1])
                    drawW = abs(self.x[i * 2] - self.x[i * 2 + 1])
                    drawH = abs(self.y[i * 2] - self.y[i * 2 + 1])
                    #qp.setPen(Qt.blue)
                    qp.drawRect(drawX, drawY, drawW, drawH)
            # 점으로 선택하는 경우
            elif self.option_method == 2:
                # 모자이크/제외 모드
                if self.mosaic_mode_flag:
                    qp.setBrush(Qt.red)#모자이크면 빨강
                else:
                    qp.setBrush(Qt.blue)#제외면 파랑
                idx = int(len(self.x))
                for i in range(idx):
                    drawX = self.x[i]
                    drawY = self.y[i]
                    qp.drawEllipse(drawX, drawY,10,10)

            ###########################</2번째 요구>####################################

            self.input_label.setPixmap(self.pixmap)

    # 변환버튼 클릭시 발생하는 이벤트
    def btn_convers_clicked(self):
        self.make_dir()
        # 좌표 선택 활성화
        self.flag = True

        '''
        <2번째 요구사항으로 인한 추가>
            '중앙'은 사실 '점'을 라벨의 중앙을 선택한 특수한 경우이다.
            '중앙'인 경우에는 좌표 선택을 막아놓아서 멤버변수 ,x, y, original_x, original_y가 비어있다.
            그러므로 여기에 라벨의 중앙값을 넣어준다.
        '''
        ######### <2번째 요구 추가>############
        if self.option_method == 1:  # 중앙
            self.x=[];self.y=[];self.original_x=[];self.original_y=[];
            self.x.append(self.input_label_width / 2)
            self.y.append(self.input_label_height / 2)
            self.original_x.append(self.width / 2)
            self.original_y.append(self.height / 2)
         ############</추가>##############



        if (len(self.file_paths) == 1 and len(self.errorResult) == 0):  # 한 개만 선택되면 좌표선택 활성화
            '''선택지가 많아지다보니 버튼 활성화가 안쓰입니다.. '''
            #self.buttonActive(False, self.btn_convers, True, self.btn_sel_pos)
            #self.buttonActive(self.mosaic_mode_flag, self.btn_mosaic_area, self.hero_mode_flag, self.btn_cent)
            self.file_path = self.file_paths[0]
            self.FindFace()
            if not (self.ErrorMsg == ""):
                QMessageBox.warning(self, "출력 에러 발생", self.ErrorMsg, QMessageBox.Yes)
                ############################### 희주 - 에러메세지 로그 출력 #########################
                # <preparation for change>
                if (self.errsaveFlag == True):
                    self.errLog = self.errLog + "\n\n---------<출력 에러>--------\n"
                    self.errLog = self.errLog + (self.ErrorMsg + '\n')
                # </preparation for change>
                self.ErrorMsg = ""

                '''좌표 선택좌 모자이크 선택이 한 장 모드, 여러장 모드에 다 쓰이니까 flag는 변환 맨 아래에서 초기화 '''
                # self.selFlag = False
                # self.mosaic_sel_flag = False

            '''
            <2번째 요구사항으로 인한 변경>
                이제 이미지 하나 선택할 때에만 좌표 제외 선택이 아니라 여러장에도 적용할 것이므로
                한 장 모드 뿐만 아니라 여러장 모드일 때에도 변환 과정을 다 마치고 초기화 시키기 위해
                btn_convers_clicked의 아래쪽으로 옮김.
                mosaic~변수들은 앞서 언급했듯 사용하지 않아서 초기화 그냥 없앰

            <기존 코드>
                 if (len(self.x) > 0):
                    self.selFlag = False
                    self.x = []
                    self.y = []
                    self.original_x = []
                    self.original_y = []
                if (len(self.mosaic_x) > 0):
                    self.mosaic_sel_flag = False
                    self.mosaic_x = []
                    self.mosaic_y = []
                    self.mosaic_origin_x = []
                    self.mosaic_origin_y = []
            '''

            self.update()
        # self.update()
        else:
            '''선택지가 많아지다보니 버튼 활성화가 안쓰입니다.. '''
            #self.buttonActive(False, self.btn_sel_img, False, self.btn_convers)
            #self.buttonActive(False, self.btn_help, False, self.btn_exit)
            #self.buttonActive(False, self.btn_mosaic_area)
            for i in range(len(self.file_paths)):
                # self.update()
                self.file_path = self.file_paths[i]
                self.FindFace()
                self.repaint()
                ############################### 예솔 - 라벨에 이미지 띄우기 여부 #########################
                # <preparation for change>
                if not (self.ys_flag): sleep(0.5)
                # </preparation for change>

            if not (self.ErrorMsg == ""):
                QMessageBox.warning(self, "출력 에러 발생", self.ErrorMsg, QMessageBox.Yes)
                ############################### 희주 - 에러메세지 로그 출력 #########################
                # <preparation for change>
                if (self.errsaveFlag == True):
                    self.errLog = self.errLog + "\n\n---------<출력 에러>--------\n"
                    self.errLog = self.errLog + (self.ErrorMsg + '\n')
                # </preparation for change>
                self.ErrorMsg = ""
            QMessageBox.information(self, "알림", "이미지 변환을 모두 마쳤습니다.", QMessageBox.Yes)
            #self.buttonActive(True, self.btn_sel_img)
            #self.buttonActive(True, self.btn_help, True, self.btn_exit)

        '''
        <2번째 요구사항으로 인한 변경>
            초기화 여기로 옮겨졌다.
            hero_flag는 사용하지 않는다.
        '''

        if (len(self.x) > 0):
            self.selFlag = False
            self.x = []
            self.y = []
            self.original_x = []
            self.original_y = []

        #if (self.hero_flag == True):
        #    self.hero_flag = False


        ############################### 희주 - 에러메세지 로그 출력 #########################
        # <preparation for change>
        if (self.errLog and self.errsaveFlag == True):
            os.chdir(self.dirName)
            fw = open('errorLog.txt', 'a+')
            fw.write(self.errLog)
            fw.close()
            self.errLog = ""
            os.chdir(self.dirName + "/../../")
            # </preparation for change>

    def FindFace(self):
        # 얼굴 찾기
        #############################소영-opencv한글 경로 안되는거 수정######################
        # 원래 이랬다가 opencv가 한글경로를 지원해주지 않아서 이미지 읽기와 저장은 모두 다른 함수를 사용합니다 ㅠ
        # image = cv2.imread(self.file_path)
        pil_image = Image.open(self.file_path)  # pillow의 Image로 이미지를 open한 후에 이를 opencv데이터 형으로 변환합니다.
        '''
        <2번째 요구사항으로 인한 변경>
            배치모드에서 모자이크/제외 기능 사용으로 여러장일 때도 사진의 사이즈를 알아야한다.
             그래서 아래에 이미지 사이즈를 알아내는 구문 추가
        '''
        (self.width, self.height) = pil_image.size #이미지의 크기 변경
        pil_image2 = Image.new('RGB', (self.width, self.height))
        pil_image2.paste(pil_image)

        ### 181110 기연 추가 ###
        if self.over_size == 1:  # 사이즈 5000 넘었을때
            pil_image2 = pil_image2.resize((200, 200))  # 이미지 (500 X 500)으로 축소
        image = cv2.cvtColor(numpy.array(pil_image2), cv2.COLOR_RGB2BGR)  # opencv의 기준은 bgr입니다.
        ########################################################################
        image_gs = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        '''
        <2번째 요구사항으로 인한 변경>
            -mosaic~변수들은 사용하지 않는다.
            -기존에 mosaic해야할 부분을 잘라서 cascade에 적용했는데
             이제는 좌표 제외와 유사하게 선택한 사각형 만나는지 아닌지로 판단한다.
             그래서 image_gs를 roi하는 것도 사용x
        '''

        #if self.mosaic_sel_flag and (len(self.mosaic_x) == 2):
        #    m_x1 = min(self.mosaic_origin_x)
        #    m_x2 = max(self.mosaic_origin_x)
        #    m_y1 = min(self.mosaic_origin_y)
        #    m_y2 = max(self.mosaic_origin_y)
        #    image_gs = image_gs[m_y1:m_y2, m_x1:m_x2]

        cascade = cv2.CascadeClassifier(self.cascade_file)
        face_list = cascade.detectMultiScale(image_gs, scaleFactor=1.1, minNeighbors=1, minSize=(75, 75))

        if len(face_list) == 0:  # 얼굴 없음
            ############################### 예솔 - 라벨에 이미지 띄우기 여부 #########################
            # <preparation for change>
            if self.ys_flag:
                self.flag = False
            else:
                w1 = self.input_label_width  # 모자이크 이미지는 findFace에서 그려짐
                h1 = self.input_label_height
                self.pixmap = QPixmap(self.file_path).scaled(w1, h1)
                self.output_label.setPixmap(self.pixmap)
            self.errOutput(4)
            # </preparation for change>

        else:
            ############################### 예솔 - 라벨에 이미지 띄우기 여부 #########################
            # <preparation for change>
            self.flag = True
            self.update()
            # </preparation for change>
            mosaic_rate = 50  # 모자이크 크기 정도
            mosaic_flag = False  # 모자이크 할것인가?
            if (len(self.x) == 0 and self.selFlag):
                self.selFlag = False
                #print("선택된 좌표가 없다.")
                #print(face_list)


            '''
                <2번째 요구사항으로 인한 변경>
                    (기존)
                        기존 주인공 제외 나머지 모자이크 함수인 find_cent는 얼굴들의 평균값을 구하고
                        이 평균값에 가장 가까운 얼굴의 x,y좌표를 반환함.

                    (변경)
                        face_list에서 선택된 점에 가까운 얼굴 pnum개 만큼 찾아주는 find_dist는
                        face_list길이의 bool list를 반환함 (true : 가까움, false : 멀다)
            '''
            ############################### 희주 - 주인공 제외 나머지 모자이크 #########################
            # <preparation for change>
            #mid_x = -1
            #mid_y = -1
            #if self.hero_flag == True:
            #    mid_x, mid_y = self.find_center(face_list)  # 중간 x값을 리턴함.
                # print(mid_x)
                # print(mid_y)
            # </preparation for change>


            '''
                <2번째 요구사항으로 인한 변경>
                    pnum과 face_list의 길이를 비교하고 점과 중앙인 경우, 멤버변수 x의 길이가 0보다 크면
                    face_list 중 점과 중앙에서 pnum개 가까운 얼굴은 true, 그 외는 false인 리스트를 face_result에 담음
                    (참고로 점 여러개인건 find_dist에서 계산되기 때문에 face_result는 점 여러개인 경우까지 다 한
                    정말 총 결과를 나타냄)
            '''

            face_result = [True] * len(face_list) #일단 다 모자이크다!(모자이크 영역 기준임)
            if self.option_method is not 0:
                if self.pnum is 0 :
                    #모자이크 영역 선택인 경우 선택한 영역이 없으니 모두 모자이크 하지 말아야 함.
                    #모자이크 제외인 경우 선택한 영역이 없으니 모두 모자이크
                    face_result = [False] * len(face_list)
                elif self.pnum >= len(face_list) :
                    #모자이크 영역 선택인 경우, 전부 선택되었으니 모두 모자이크
                    #제외 영역 선택인 경우, 모두 선택했으니 모두 모자이크 x
                    face_result = [True] * len(face_list)
                elif (len(self.x) > 0):
                    face_result = self.find_Dist(face_list)
            #########################

            '''
                <2번째 요구사항으로 인한 변경>
                    선택한 점(혹은 중앙)에서 가까운 얼굴인지 아닌지를 face_result라는 bool 타입 list로 알아본다.
                    (true : 가까움 / false:멀다)
                    그래서 face_list의 인덱스 값은 face_idx라는 변수에 추가하였다.
                </>

                <기존 코드>
                for (x, y, w, h) in face_list:
                </>
            '''
            # print(len(face_list))
            for face_idx, (x, y, w, h) in enumerate(face_list):#인덱스 추가!!!!!!!!!!!!!!!
                '''mosaic기능이 선택 영역에만 cascade 적용하는거에서 face_list와 모자이크 영역이 겹치는지 비교하는
                방법으로 바뀌어서 아래거 안쓰인다.
                '''
                #if ((self.mosaic_sel_flag == True) and (len(self.mosaic_x) == 2)):
                #    x = x + min(self.mosaic_origin_x)
                #    y = y + min(self.mosaic_origin_y)

                    # print(x)
                    # print(y)
                #print(type(x))
                ### 181110 기연 추가 ###
                if self.over_size_flag and self.over_size == 1:
                    multiple_rate_width = self.width / 200  # 500으로 작아진 이미지의 가로사이즈가 원본과 몇 배차이인지
                    multiple_rate_height = self.height / 200  # 500으로 작아진 이미지의 세로사이즈가 원본과 몇 배차이인지
                    x = x * int(multiple_rate_width)  # 각각 원본이미지에 맞춰 키우기
                    y = y * int(multiple_rate_height)
                    w = w * int(multiple_rate_width)
                    h = h * int(multiple_rate_height)
                '''
                <2번째 요구사항으로 인한 변경>
                    -(기존) 좌표 선택이 됐는지 알아보고 선택됐다면 좌표와 얼굴이 겹치는지 본다.
                    -(변경) 모드가 늘어나서 여러 경우를 봐야함.
                    좌표가 선택됐는지 본다.-> 모자이크/제외 모드 확인->사각형/점/중앙 확인
                </>

                <기존 코드>
                    if (len(self.x) < 1):  # 따로 선택된 좌표가 없음
                        mosaic_flag = True  # 모자이크 한다.
                    else:
                        if (self.calRect(x, y, w, h) == 1):  # 좌표를 선택했는데 그거랑 얼굴이랑 안겹침
                            mosaic_flag = True  # 모자이크 한다.
                </>
                '''
                #print("findface의 {0}번째 얼굴 탐색".format(face_idx))

                ###################<2번째요구>####################
                if (len(self.x) < 1):  # 따로 선택된 좌표가 없음
                    mosaic_flag = True  # 모자이크 한다.
                else:#선택된 좌표가 있다.
                    if(self.mosaic_mode_flag): #모자이크 모드
                        if self.option_method == 0:#사각형인 경우
                            if (self.calRect(x, y, w, h) == 0):  # 좌표를 선택했는데 그거랑 얼굴이랑 겹침
                                mosaic_flag = True  # 모자이크 한다.
                        else: #중앙이나 점 선택인 경우
                            #모자이크 모드에서는 선택 영역과 가까운걸 모자이크한다.
                            mosaic_flag = face_result[face_idx] #가까운게 true 먼게 false임
                    else: #좌표 제외 모드
                        if self.option_method == 0:
                            if (self.calRect(x, y, w, h) == 1):  # 좌표를 선택했는데 그거랑 얼굴이랑 안겹침
                                mosaic_flag = True  # 모자이크 한다.
                        else:#중앙이나 점
                            #가까운게 좌표 제외되어야 한다.
                            mosaic_flag = not face_result[face_idx]#가까운게 true니까 이거랑 반대로 가까운건 false여야함

                ############################### 희주 - 주인공 제외 나머지 모자이크 #########################
                # <preparation for change>
                #if (self.hero_flag and (x == mid_x) and (y == mid_y)):
                #    mosaic_flag = False
                    # self.hero_flag = False
                    # </preparation for change>
            ###################</2번째요구>####################

                ### 181112 예솔 추가 ###
                if (mosaic_flag):
                    # 모자이크
                    ### 181110 기연 추가 ###
                    if self.over_size_flag and self.over_size == 1:  # 원본이미지 다시 갖고오기.
                        pil_image = Image.open(self.file_path)
                        image = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
                    if self.ys_rp_flag:
                        face_img = cv2.resize(self.rp_img, (w, h), interpolation=cv2.INTER_AREA)
                    else:
                        face_img = image[y:y + h, x:x + w]
                        ### 181110 기연 추가 ###
                        if self.over_size_flag and self.over_size == 1:  # 큰 사진이라 좀 크게줌
                            face_img = cv2.resize(face_img, (w // 200, h // 200))
                        else:
                            face_img = cv2.resize(face_img, (w // mosaic_rate, h // mosaic_rate))
                        face_img = cv2.resize(face_img, (w, h), interpolation=cv2.INTER_AREA)
                    image[y:y + h, x:x + w] = face_img
                    mosaic_flag = False

            # 모자이크한 이미지 저장

            f_split = self.file_path.split('/')
            f_split = f_split[len(f_split) - 1].split('.')
            saveName = f_split[0] + "_mosaic.jpg"
            ############################### 혜나 - 파일을 다른 이름으로 저장 #########################
            # 파일을 다른이름으로 저장 할 시
            # <preparation for change>
            if (self.hn_flag == True):
                file_name = QFileDialog.getSaveFileName(self, "Save File", self.dirName)
                file_name, _ = file_name
                file_name = file_name.split('/')
                file_name = file_name[len(file_name) - 1]
                file_name = file_name + '.jpg'
                saveName = file_name
                #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                #saveim = Image.fromarray(image)
                #saveim.save(os.path.join(self.dirName, saveName))
                # </preparation for change>
            #else:
                #############################소영-opencv한글 경로 안되는거 수정######################
                # cv2.imwrite(os.path.join(self.dirName, saveName), image) 한글 경로는 저장도 안됨 ㅠ
                #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                #saveim = Image.fromarray(image)
                #saveim.save(os.path.join(self.dirName, saveName))  # opencv 데이터를 pillow Image로 바꿔서 경로에 저장한다.
                #######################################################
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            saveim = Image.fromarray(image)
            saveim.save(os.path.join(self.dirName, saveName))
            # 저장한 이미지를 불러 output_label에 넣는다.
            w = self.output_label.width()
            h = self.output_label.height()
            save_path = "./" + self.dirName + "/" + saveName
            # pixmap = QPixmap("mosaic_image.jpg")
            pixmap = QPixmap(save_path)
            self.output_label.setPixmap(pixmap.scaled(w, h))
            ############################### 예솔 - 라벨에 이미지 띄우기 여부 #########################
            # <preparation for change>
            if (self.ys_flag):
                sleep(0.5)
                # </preparation for change>

    def calRect(self, x, y, w, h):  # 안겹치면1, 겹치면 0을 반환한다.
        # print(len(self.original_x))

        x = x / self.width * self.input_label_width
        y = y / self.height * self.input_label_height
        w = w / self.width * self.input_label_width
        h = h / self.height * self.input_label_height

        idx = 1  # 기본은 좌표 선택 하나임

        if (self.multi_flag == True):  # 좌표 선택 여러개 할 수 있는 경우
            idx = int(len(self.x) / 2)

        for i in range(idx):
            e_x = [min(self.x[i * 2], self.x[i * 2 + 1]),
                   max(self.x[i * 2], self.x[i * 2 + 1])]  # 모자이크 제외 영역
            e_y = [min(self.y[i * 2], self.y[i * 2 + 1]),
                   max(self.y[i * 2], self.y[i * 2 + 1])]
            m_x = [x, x + w]  # 원래라면 모자이크 되었어야할 영역
            m_y = [y, y + h]

            if ((e_x[0] > m_x[1]) or (e_x[1] < m_x[0]) or (e_y[0] > m_y[1]) or (
                e_y[1] < m_y[0])):  # 모자이크영역과 선택 좌표가 겹치지 않을 조건
                pass
            else:  # 모자이크 영역과 선택좌표가 겹치는 경우
                return 0

        return 1;  # 반복문을 다 돌았는데 끝나지 않았다면 모자이크 영역과 선택 영역이 겹치지 않은거임.

    '''
        <2번째 요구에 의한 변경>
            getCoor은 getcoor_flag에 따라서 좌표/모자이크 영역 선택 중 어떤 것인지에 따라 input_label 클릭 시
            호출되는 함수를 달리하는 함수임.
            기존에 모자이크 선택과 좌표제외 선택이 구분되어 대비되었기 때문에 input_label에서 발생하는 이벤트도
            구분해야할 필요가 있었으나 이제 합쳐져서 필요x
        </>

        def getCoor(self, event):
        if (self.getcoor_flag == False):
            self.getPixel(event)
        elif (self.getcoor_flag):
            self.get_mosaicPixel(event)
    '''
    # input_label에서 클릭한 좌표 얻기
    def getPixel(self, event):
        if (self.selFlag):
            # txt = "Mouse 위치; x={0},y={1},global={2},{3}".format(event.x(), event.y(), event.globalX(), event.globalY())

            if (self.multi_flag):
                self.x.append(event.x())
                self.y.append(event.y())
                self.original_x.append(int((event.x() / self.input_label_width) * self.width))
                self.original_y.append(int((event.y() / self.input_label_height) * self.height))
            else:
                if (len(self.x) < 2):
                    self.x.append(event.x())
                    self.y.append(event.y())
                    self.original_x.append(int((event.x() / self.input_label_width) * self.width))
                    self.original_y.append(int((event.y() / self.input_label_height) * self.height))
                else:
                    # print("이미 선택된 좌표가 있습니다. x좌표들 {0}, y좌표들 {1}".format(self.x,self.y))
                    self.errOutput(5)

                # 변환 버튼 활성화 조작
                if (len(self.x) == 0 or len(self.x) == 2):
                    self.coordFlag = True
                else:
                    self.coordFlag = False

                #self.buttonActive(self.coordFlag, self.btn_convers)


                ############################### 소영(2) - 모자이크 될 영역만 선택 #########################
    '''

        <2번째 요구에 의한 변경>
            get_mosaicPixel은 모자이크 영역 좌표 선택을 받는 함수임.
            기존에 모자이크 선택과 좌표 제외 선택이 구분되어 대비되었기 때문에 getPixel함수와
            구분해야할 필요가 있었으나 이제 getPixel로 모자이크 영역 좌표를 입력받아서 필요x
        </>

        # <preparation for change>
    def get_mosaicPixel(self, event):
        # self.mosaic_sel_flag = True
        if (self.mosaic_sel_flag):
            if (len(self.mosaic_x) < 2):
                self.mosaic_x.append(event.x())
                self.mosaic_y.append(event.y())
                self.mosaic_origin_x.append(int((event.x() / self.input_label.width()) * self.width))
                self.mosaic_origin_y.append(int((event.y() / self.input_label.height()) * self.height))
            else:
                # print("이미 선택된 좌표가 있습니다. x좌표들 {0}, y좌표들 {1}".format(self.x,self.y))
                self.errOutput(5)

    # </preparation for change>
    '''


    def btn_sel_pos_clicked(self):  # 좌표선택
        if self.selFlag is False:
            self.selFlag = True
            #self.mosaic_sel_flag = False
            #self.getcoor_flag = False

        # 좌표 선택 버튼 비활성화
        self.x = []
        self.y = []
        self.original_x = []
        self.original_y = []
        #self.buttonActive(True, self.btn_convers, False, self.btn_sel_pos)
        # self.buttonActive(True, self.btn_mosaic_area)

    def btn_help_clicked(self):
        # ctypes.windll.user32.MessageBoxW(0, "여기는 도움말 입니다.", "도움말", 1)
        # buttonReply = QMessageBox.question(self, 'PyQt5 message', "Do you like PyQt5?",
        #                                   QMessageBox.Yes | QMessageBox.Help, QMessageBox.Help)
        # QMessageBox.question(self,"도움말","여기는 도움말 입니다",QMessageBox.Yes)
        helpMessage = "\n\n(1) 프로그램 종료 방법 : 좌측 상단의 종료 버튼 또는 우측 상단의 x버튼 클릭시 프로그램이 종료됩니다." \
                      "\n\n(2) 이미지 선택 : 이미지 선택 버튼을 클릭 후 파일 탐색창을 통해 이미지를 선택할 수 있습니다." \
                      "\n\n(3) 모드 선택 : 모자이크 제외영역 또는 모자이크 영역을 선택할 수 있습니다." \
                      "\n\n(4) 좌표 선택 방법 : 모드 선택에 따라 영역 선택방법을 고를 수 있습니다." \
                      "\n사각형을 선택시 좌표선택을 통해 한개 또는 여러개의 사각형을 그릴 수 있습니다." \
                      "\n중앙을 선택시 사진 가운데로부터 제외 또는 모자이크 영역이 설정됩니다." \
                      "\n점을 선택시 한개 또는 여러개의 점을 그릴 수 있습니다. 해당 점으로부터 제외 또는 모자이크 영역이 설정됩니다." \
                      "\n\n(5) 인원수 선택 : 중앙 또는 점을 선택했을 경우 제외 또는 모자이크영역에 포함되는 인원을 선택할 수 있습니다.\n\n"
        QMessageBox.information(self, "도움말", helpMessage, QMessageBox.Yes)

    def btn_exit_clicked(self):
        sys.exit(0)

        ############################### 소영(2) - 모자이크 될 영역만 선택 #########################


    '''

        <2번째 요구에 의한 변경>
            모자이크 영역 선택 버튼이 모자이크 영역 선택 라디오버튼으로 UI가 변경되면서
             버튼 클릭시 발생하는 함수인 btn_mosaic_area_clicked의 기능도 ModeRadioGroupClicked로 편입되었다.
        </>

        # <preparation for change>
        def btn_mosaic_area_clicked(self):
        if (self.mosaic_sel_flag == False):
            self.mosaic_sel_flag = True
            self.selFlag = False
            self.getcoor_flag = True

        self.mosaic_x = []
        self.mosaic_y = []
        self.mosaic_origin_x = []
        self.mosaic_origin_y = []
        #self.buttonActive(True, self.btn_convers, False, self.btn_mosaic_area)
        # </preparation for change>

    '''

        ############################### 희주 - 주인공 제외 나머지 모자이크 #########################

    # <preparation for change>
    '''
        <2번째 요구에 의한 변경>
            주인공 제외 선택 버튼이 '중앙' 선택 라디오버튼으로 UI가 변경되면서
             버튼 클릭시 발생하는 함수인 btn_cent_clicked의 기능도 SelRadioBtnClicked로 편입되었다.
        </>

        def btn_cent_clicked(self):
            self.hero_flag = True

            #self.buttonActive(True, self.btn_convers, False, self.btn_sel_pos)  # 변환 버튼만 활성화
            #self.buttonActive(False, self.btn_mosaic_area, False, self.btn_cent)
    '''
    '''
        <2번째 요구에 의한 변경>
            face_list를 입력받아 얼굴들의 평균 좌표를 구한 후, 해당 좌표에서 가장 가까운 거리의 얼굴을 계산해
            이 얼굴의 x,y좌표를 반환하는 방식에서 face_list와 선택한 좌표들(멤버변수 x,y)에서 pnum개 만큼 가까운
            얼굴들은 true, 그 외에는 false로 한 bool 타입 list를 반환하는 방식으로 확장.
            find_cent -> find_dist
        </>


    def find_center(self, face_list):  # 얼굴들 사이의 중앙값에 가까운 순으로 pnum개만큼 true하고 결과 리턴
        list_length = len(face_list)
        x_list = [row[0] for row in face_list]  # face_list의 0번째 열
        y_list = [row[1] for row in face_list]  # face_list의 1번째 열
        self.x_sum = 0
        self.y_sum = 0
        for i in x_list:
            self.x_sum += i
        for i in y_list:
            self.y_sum += i

        self.x_avg = int(self.x_sum / len(x_list))  # x좌표들의 평균
        self.y_avg = int(self.y_sum / len(y_list))  # y좌표들의 평균
        distance = []
        for i in range(len(x_list)):
            distance.append(int(abs(self.x_avg - x_list[i]) + abs(self.y_avg - y_list[i])))

        for i in range(len(x_list)):
            if (min(distance) == distance[i]):
                result = []
                result.append(x_list[i])
                result.append(y_list[i])
                return result
                # </preparation for change>
    '''

    ######<2번째 요구 >###############################
    '''각 라디오 그룹별로 함수를 만들어 관리한다. UI변경에 의해 추가된 함수'''
    #######모자이크/제외 라디오 그룹 선택시####
    def ModeRadioGroupClicked(self):
        if self.btn_except_area.isChecked():
            print("radio exception is clicked")
            self.mosaic_mode_flag = False
        elif self.btn_mosaic_area.isChecked():
            print("radio mosaic is clicked")
            self.mosaic_mode_flag = True

    #######사각, 중앙, 점 선택 ###############
    def SelRadioGroupClicked(self):
        if self.btn_rect.isChecked():
            print("사각")
            self.option_method = 0
            self.buttonActive(self.flag, self.btn_sel_pos, False, self.btn_pnum)
        elif self.btn_cent.isChecked():
            print("중앙")
            self.option_method = 1
            self.buttonActive(False, self.btn_sel_pos, True, self.btn_pnum)
        elif self.btn_point.isChecked():
            print("점")
            self.option_method = 2
            self.buttonActive(self.flag, self.btn_sel_pos, True, self.btn_pnum)
        #### 사람 인원 수 선택 ####
    def PnumComboClicked(self):
        txt = self.btn_pnum.currentText()
        idx = self.btn_pnum.currentIndex()
        self.pnum = idx
        print("콤보 박스의 {0}번째 인덱스가 선택되었습니다. 값은 {1}".format(idx,txt))

    ######face_list에서 self.x, self.y에 가까운 좌표를 pnum의 개수만큼 검사한다.
    def find_Dist(self, face_list):  # x,y 에서 가까운 값 찾아서 인덱스 반환
        #if self.pnum >= list_length: # pnum의 개수가 검출된 얼굴 수 보다 크다면 그냥 전부 모자이크하면 된다.
        #이걸 제외한 나머지 경우로 가정한다. 즉, pnum < list_length

        list_length = len(face_list)
        x_list = [row[0] for row in face_list]  # face_list의 0번째 열
        y_list = [row[1] for row in face_list]  # face_list의 1번째 열
        w_list = [row[2] for row in face_list]  # face_list의 2번째 열
        h_list = [row[3] for row in face_list]  # face_list의 3번째 열
        print(x_list)

        for i in range(list_length):#좌표를 라벨 사이즈에 맞게 변환
            x_list[i] = (x_list[i]+w_list[i]/2) / self.width * self.input_label_width
            y_list[i] = (y_list[i]+h_list[i]/2) / self.height * self.input_label_height

        print(x_list)
        result = [False] * list_length #결과 list를 face_list 길이 만큼 False로 초기화


        for i in range(len(self.x)): #선택한 좌표 만큼 돌린다.
            distance = []
            for j in range(list_length):#i번째 좌표에서 얼굴들 거리를 구한다.
                distance.append(pow(self.x[i] - x_list[j],2) + pow(self.y[i] - y_list[j],2))

            min_dist = sorted((e, k) for k, e in enumerate(distance))#거리 정렬
            #distance가 오름차순으로 정렬되는데 그냥 정렬되는게 아니라 해당 값이 이전에 어떤 인덱스를 가졌는지도 함께 가짐
            #enumerate가 인덱스의 값은 k, 정렬 값은 e에 저장한다
            #예로들어 distance = [1,3,5,2,4]라면 min_dist = [(1, 0), (2, 3), (3, 1), (4, 4), (5, 2)]이다.

            for j in range(self.pnum):
                idx = min_dist[j][1]#i번째 좌표에서 j번째로 가까운 얼굴의 face_list에서의 인덱스값
                result[idx] = True #가깝다!
                print("{0}번째 얼굴 빠짐".format(idx))

        return result
    ######</2번째 요구>###############################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()