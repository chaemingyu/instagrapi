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
import threading
from Core.InstagrAPI import InstagrAPI
from Core import Config
from concurrent.futures import ThreadPoolExecutor
import time

class ThreadJob:
    _instance = None  # _instance을 미리 정의해야 함

    @staticmethod
    def GetInstance():
        if ThreadJob._instance is None:
            ThreadJob._instance = ThreadJob()
        return ThreadJob._instance

    def __init__(self):

        self.insta = InstagrAPI.GetInstance()

        # 스레드 초기화
        self.Followthread = threading.Thread(target=self.FollowingWork)
        self.Followthread.daemon = True  # 데몬 스레드 설정 (프로그램 종료 시 함께 종료)

        self.Loginthread = threading.Thread(target=self.ReLoginWork)
        self.Loginthread.daemon = True  # 데몬 스레드 설정 (프로그램 종료 시 함께 종료)

        self.GetOrderthread = threading.Thread(target=self.GetOrders)
        self.GetOrderthread.daemon = True  # 데몬 스레드 설정 (프로그램 종료 시 함께 종료)


    def start(self):
        # 스레드 시작
        self.Loginthread.start()
        self.Followthread.start()
        self.GetOrderthread.start()
        pass
    def stop(self):
        self.Loginthread.thread_should_run = False  # 스레드 종료를 위해 플래그 변경
        self.Followthread.thread_should_run = False  # 스레드 종료를 위해 플래그 변경
        self.GetOrderthread.thread_should_run = False  # 스레드 종료를 위해 플래그 변경
        
    #region == GetOrders() [주문정보 얻어오기] ==
    def GetOrders(self):
        try: 
            #일단 텍스트 파일에서 읽어오기
            #나중에 api 방식으로 가져오는 기능을 모방해서 작성
            while True:
                while len(self.insta.TestIDList) > 0 and self.insta.TestIDQue.qsize() < 5:
                        target_id = self.insta.TestIDList.pop(0)  # 리스트에서 첫 번째 데이터를 가져옴
                        self.insta.TestIDQue.put(target_id)  # 큐에 데이터 추가

                #일단 대안이 없어서 2분 쉬는거로 테스트
                #프록시를 추가해 보면 가능해 보인다.
                time.sleep(120)
        except Exception as e:
             # print(f'Login 에러 발생: {e}')
            return f'GetOrders 에러 발생: {e}'
        

    #endregion
    

    def FollowingWork(self):

        try:
            while True:
                # 큐에서 데이터 가져오기 (무한 대기)
                tagetid = self.insta.TestIDQue.get()

                #소비자 실행(큐 소비)
                #start_time = time.time()  # 작업 시작 시간 기록

                #병렬 작업 등록(풀링)
                #각 작업 대상 id별로 팔로우 작업을 작업 계정에 동시에 등록
                results = []
                with ThreadPoolExecutor() as executor:
                    for user in self.insta.UserList:
                        result = executor.submit(self.insta.Follow, user, tagetid)
                        results.append(result)

                for future in results:
                    print(future.result())  # 결과 출력

                #end_time = time.time()  # 작업 종료 시간 기록
                #elapsed_time = end_time - start_time  # 경과 시간 계산
                #print(f"테스트 팔로우 완료되었습니다. 소요된 시간: {elapsed_time}초")

                #작업 완료후 데이터 빼기
                self.insta.TestIDQue.task_done()
                time.sleep(1)

        # except PleaseWaitFewMinutes:
        #     pass
        #
        # except LoginRequired:
        #     self.insta.UserList[1].Client.relogin()  # Use clean session
        #     # self.insta.UserList[1].Client.dump_settings(file)
        except OSError:
            print('에러: Initialize')


    # def ReLogin(self):
    #     counter = 2
    #     while (counter != 0):
    #         try:
    #             user_id = bot.user_id_from_username(PROFILE)
    #             medias = bot.user_medias(user_id)
    #             break
    #         except LoginRequired:
    #             print("Login failed. Relogging in....")
    #             bot.relogin()
    #             bot.dump_settings(SESSION_JSON)
    #             counter = counter - 1

    #재로그인
    #재로그인 대상은 큐에 담아 이리로 전달 한다.
    def ReLoginWork(self):
        try:
            while True:
                data = self.insta.ReLoginQue.get()  # 큐에서 데이터 가져오기 (무한 대기)
                # 가져온 데이터에 대한 작업 수행
                print(f"Consumed: {data}")

        except OSError:
            print('에러: ReLoginWork')