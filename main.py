import sys
from Core.InstagrAPI import InstagrAPI
from PyQt5.QtWidgets import *
from Core.ThreadJob import ThreadJob
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.Initialize()

        self.setGeometry(500, 500, 1000, 500)

        Login = QPushButton(text="로그인", parent=self)
        Login.move(10, 10)
        Login.resize(80,30)
        Login.clicked.connect(self.Login)

        Like = QPushButton(text="좋아요", parent=self)
        Like.move(100, 10)
        Like.resize(80,30)
        Like.clicked.connect(self.Like)


        self.comment_input = QLineEdit(self)  # 댓글 입력 텍스트 상자 추가
        self.comment_input.move(200, 10)
        self.comment_input.resize(200, 30)

        Comment = QPushButton(text="댓글", parent=self)
        Comment.move(420, 10)
        Comment.resize(80,30)
        Comment.clicked.connect(self.Comment)

        Follow = QPushButton(text="팔로우", parent=self)
        Follow.move(520, 10)
        Follow.resize(80,30)
        Follow.clicked.connect(self.Follow)

        Search = QPushButton(text="게시물조회", parent=self)
        Search.move(10, 80)
        Search.resize(80,30)
        Search.clicked.connect(self.Search)

        self.link_input = QLineEdit(self)  # 댓글 입력 텍스트 상자 추가
        self.link_input.move(100, 80)
        self.link_input.resize(200, 30)

        Crawling = QPushButton(text="크롤링", parent=self)
        Crawling.move(320, 80)
        Crawling.resize(80,30)
        Crawling.clicked.connect(self.Crawling)


    def Initialize(self):
        self.insta = InstagrAPI.GetInstance()
        self.insta.Initialize()
        self.Mainthread = ThreadJob.GetInstance()
        self.Mainthread.start()
    def Login(self):
        try:
            self.insta.Login()
            print('로그인 완료')
        except Exception as e:
            QMessageBox.about(self, '에러', str(e))

    def Like(self):
        try:
            link_input = self.link_input.text()
            self.insta.Like(link_input)
            print('좋아요 완료')
        except Exception as e:
            QMessageBox.about(self, '에러', str(e))

    def Comment(self):
        try:
            comment_text = self.comment_input.text()  # 입력된 댓글 텍스트 가져오기
            self.insta.Comment(comment_text)

            print('댓글 완료')
        except Exception as e:
            QMessageBox.about(self, '에러', str(e))

    def Search(self):
        try:
            link_input = self.link_input.text()
            self.insta.Search(link_input)

            print('게시물 조회 완료')
        except Exception as e:
            QMessageBox.about(self, '에러', str(e))

    def Follow(self):
        try:
            link_input = self.link_input.text()
            #self.insta.Follow(link_input)
            self.insta.FollowList()

            print('팔로우 완료')
        except Exception as e:
            QMessageBox.about(self, '에러', str(e))

    def Crawling(self):
        try:
            link_input = self.link_input.text()
            self.insta.CrawlingId()

            print('크롤링 완료')
        except Exception as e:
            QMessageBox.about(self, '에러', str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()





