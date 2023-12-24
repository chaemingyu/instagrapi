from Core.CommonAPI import CommonAPI
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    FeedbackRequired,
    LoginRequired,
    PleaseWaitFewMinutes,
    RecaptchaChallengeForm,
    ReloginAttemptExceeded,
    SelectContactPointRecoveryForm,
)
import os
import requests
from bs4 import BeautifulSoup
from Core import Config
from Core.User import User
import queue  # queue 모듈 import

class InstagrAPI(CommonAPI):
    # 싱글톤
    _instance = None

    #region Constructor()

    def __init__(self):

        # 로그인리스트
        self.UserList = []
        self.TestIDList = []
        # 테스트 계정 대상
        self.TestIDQue = queue.Queue()
        # 재 로그인 대상자
        self.ReLoginQue = queue.Queue()

        self.Initialize()

    @staticmethod
    def GetInstance():
        if InstagrAPI._instance is None:
            InstagrAPI._instance = InstagrAPI()
        return InstagrAPI._instance

    #endregion

    #region Method()

    #region == Initialize() [초기화] ==
    def Initialize(self):
        try:

            self.ReadUserList()
            print(f'계정 정보 불러오기 완료')
            self.Login()
            print('로그인 완료')
            self.ReadTestIDList()
            print('테스트 계정 정보 읽기 완료')

        except Exception as e:
             print(f'Initialize 에러 발생: {e}')
    #endregion

    #region == ReadUserList() [로그인 계정 정보 읽기] ==

    def ReadUserList(self):
        try:

            file_path = Config.LoginInfoPath
            with open(file_path, 'r') as file:
                lines = file.readlines()

            for line in lines:
                data = line.strip().split(':')[:2]  # 첫 번째와 두 번째 정보 가져오기
                print(f"계정: {data[0]} 비밀번호: {data[1]}")
                self.UserList.append(User(data[0], data[1]))

            # print(f'계정 정보 세팅 완료')

        except Exception as e:
            print(f'ReadUserList 에러 발생: {e}')

    #endregion

    # region == ReadTestIDList() [테스트 계정 정보 읽기] ==

    def ReadTestIDList(self):
        try:
            # 테스트 계정 불러오기
            file_path = Config.TestIDListPath
            with open(file_path, 'r') as file:
                self.TestIDList = [line.strip() for line in file.readlines()]

            # # 큐에 담기(생성자 소비자 패턴 사용 위함)
            # for account in test_accounts:
            #     self.TestIDQue.put(account.strip())

            # print('테스트 계정 정보 읽기 완료')

        except Exception as e:
            print(f'ReadTestIDList 에러 발생: {e}')

    # endregion

    #region == Login() [로그인(전체 계정)] ==
    def Login(self):

        try:

            # 유저 리스트 로그인
            for user in self.UserList:

                # 로그인 하지 않은 계정을 대상으로 로그인
                if user.LoginYn == 'N':
                    # 클라이언트 객체 생성(여기다 나중에 프록시 작업)
                    user.Client = Client()
                    # 계정별 세션 파일
                    session_file = os.path.join(Config.SessionFolderPath, f"{user.UserName}.json")

                    if os.path.exists(session_file):
                        user.Session = user.Client.load_settings(session_file)

                    login_via_session = False
                    login_via_pw = False

                    if user.Session:
                        try:
                            user.Client.set_settings(user.Session)
                            user.Client.login(user.UserName, user.Password)
                            # 세션이 유효한지 확인
                            try:
                                user.Client.get_timeline_feed()
                            except LoginRequired:
                                print("세션이 유효하지 않아 사용자명과 비밀번호로 로그인이 필요합니다.")
                                old_session = user.Client.get_settings()
                                # 동일한 장치 UUID를 사용하여 로그인
                                user.Client.set_settings({})
                                user.Client.set_uuids(old_session["uuids"])
                                user.Client.login(user.UserName, user.Password)
                            login_via_session = True
                        except Exception as e:
                            print("세션 정보를 사용하여 사용자 로그인 실패: %s" % e)

                    if not login_via_session:
                        try:
                            print("사용자명과 비밀번호로 로그인 시도. 사용자명: %s" % user.UserName)
                            if user.Client.login(user.UserName, user.Password):
                                user.Client.dump_settings(f"{user.UserName}.json")
                                login_via_pw = True
                        except Exception as e:
                            print("사용자명과 비밀번호로 로그인하는 데 실패했습니다: %s" % e)
                            continue

                    if not login_via_pw and not login_via_session:
                        print("비밀번호 또는 세션으로 사용자 로그인에 실패했습니다")
                        continue
                # 로그인 성공
                user.LoginYn = 'Y'
        except Exception as e:
            print(f'Login 에러 발생: {e}')

    #endregion

    #region == Follow() [팔로우] ==

    def Follow(self,user,targetid):
        try:
            print(f'사용자: {user.UserName}')
            print(f'팔로우대상: {targetid}')
            user.Client.delay_range = [1, 3]
            user_id = user.Client.user_id_from_username(targetid)

            result = f'계정명: {user.UserName}'

            if user_id:
                user.Client.user_follow(user_id)
                result += f"팔로우 성공 {targetid}"
            else:
                result += f"팔로우 실패 {targetid}"

            return result
        except LoginRequired:
            user.Client.relogin()  # Use clean session
            user.Client.dump_settings(f"{user.UserName}.json")
            return f'에러: Follow LoginRequired'
        # except LoginRequired:
        #     self.ReLoginQue.put(user)
        #     return f'에러: Initialize'
        except Exception as e:
            # print(f'Login 에러 발생: {e}')
            return f'Follow 에러 발생: {e}'

    #endregion

    #region == Logger() [재 로그인] ==

    def ReLogin(self,user,line):
        try:

            return f'사용자: {user.UserName} 팔로우대상: {line.strip()}'
        except LoginRequired:
            user.Client.relogin()  # Use clean session

            return f'에러: Initialize'
        except OSError:
            return f'에러: Initialize'
            #print('에러: Initialize')

    #endregion

    #endregion



    # def FollowList(self):
    #     try:
    #         # start_time = time.time()  # 작업 시작 시간 기록
    #
    #         #id 추출
    #         file_path = Config.FollowListPath
    #
    #         with open(file_path, 'r') as file:
    #             self.FollowList = file.readlines()
    #
    #         for line in self.FollowList:
    #             self.UserList[1].Client.delay_range = [1, 3]
    #             # print(line.strip())  # 각 줄의 데이터 출력 (strip()으로 공백 제거)
    #             user_id = self.UserList[1].Client.user_id_from_username(line.strip())
    #             if user_id:
    #                 print(self.UserList[1].Client.user_follow(user_id))
    #                 print(f"Following {user_id}")
    #             else:
    #                 print(f"User {user_id} not found")
    #
    #
    #         # end_time = time.time()  # 작업 종료 시간 기록
    #         # elapsed_time = end_time - start_time  # 경과 시간 계산
    #         #
    #         # print(f"작업이 완료되었습니다. 소요된 시간: {elapsed_time}초")
    #
    #     except OSError:
    #         print('에러: Initialize')
    #


    # def Search(self,username):
    #
    #     try:
    #         #조회
    #         self.cl.delay_range = [1, 3]
    #         # self.user_id = self.cl.user_id_from_username(self.LoginInfo[0])
    #         self.user_id = self.cl.user_id_from_username(username)
    #         print(self.user_id)
    #         self.medias = self.cl.user_medias(self.user_id, 20)
    #         print(self.medias)
    #     except OSError:
    #         print('Error: Like ')
    #
    #
    # def Like(self,link):
    #
    #     try:
    #         print("Liking...")
    #         # print(link)
    #         # self.cl.media_like(str(link))
    #         for media in self.medias:
    #             print("Liking...")
    #             print(media.model_dump()['pk'])
    #             self.cl.media_like(media.model_dump()['pk'])
    #         #    self.cl.media_like(link)
    #     except OSError:
    #         print('Error: Like ')
    #
    # def Comment(self, comment_text=None):
    #     try:
    #         for media in self.medias:
    #             print("Commenting...")
    #             if not comment_text:
    #                 comment_text = '테스트 안녕하세요!?'  # 입력된 값이 없으면 기본값으로 설정
    #             else:
    #                 print(f"Comment Text: {comment_text}")  # 입력된 값이 있으면 출력
    #
    #             self.cl.media_comment(media.model_dump()["pk"], comment_text)  # 댓글 작성
    #
    #     except OSError:
    #         print('Error: Comment')
    #
    # def Follow(self, username):
    #     try:
    #
    #         user_id = self.cl.user_id_from_username(username)
    #         if user_id:
    #             self.cl.user_follow(user_id)
    #             print(f"Following {username}")
    #         else:
    #             print(f"User {username} not found")
    #
    #     except LoginRequired:
    #         self.cl.relogin()  # Use clean session
    #
    #
    # def CrawlingId(self):
    #     # 웹 페이지 URL
    #     url = 'https://www.instagram.com/'
    #
    #     # 웹 페이지에 요청을 보냄
    #     response = requests.get(url)
    #
    #     # 요청이 성공했는지 확인
    #     if response.status_code == 200:
    #         # BeautifulSoup으로 HTML 파싱
    #         soup = BeautifulSoup(response.text, 'html.parser')
    #
    #         # 클래스를 이용하여 요소 선택
    #         css_class = '#mount_0_0_PA > div > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x9f619.xvbhtw8.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.x1q0g3np.xqjyukv.x1qjc9v5.x1oa3qoh.x1qughib > div.x1gryazu.xh8yej3.x10o80wk.x14k21rp.x17snn68.x6osk4m.x1porb0y > section > main > div > div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.xwib8y2.x1y1aw1k.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1 > div > div > div:nth-child(1) > div > div > div > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x1iyjqo2.xs83m0k.xeuugli.x1qughib.x6s0dn4.x1a02dak.x1q0g3np.xdl72j9 > div > div > div > div > div > a > div > div > span'
    #         target_elements = soup.find_all(class_=css_class)
    #
    #         # 찾은 요소의 텍스트 출력
    #         if target_elements:
    #             print(target_element.text)
    #         else:
    #             print("해당하는 요소를 찾을 수 없습니다.")
    #     else:
    #         print("페이지를 가져오는 데 문제가 발생했습니다. 상태 코드:", response.status_code)