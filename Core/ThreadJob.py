from instagrapi.exceptions import (
    LoginRequired,
)
import threading
from Core.InstagrAPI import InstagrAPI
from Core import Config
from concurrent.futures import ThreadPoolExecutor


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

    def start(self):
        # 스레드 시작
        # self.Loginthread.start()
        # self.Followthread.start()
        pass
    def stop(self):
        self.Loginthread.thread_should_run = False  # 스레드 종료를 위해 플래그 변경
        self.Followthread.thread_should_run = False  # 스레드 종료를 위해 플래그 변경


    def Follower(self,user,line):
        try:
            print(f'사용자: {user}')
            print(f'팔로우대상: {line}')
            # user.Client.delay_range = [1, 3]
            # user_id = user.Client.user_id_from_username(line.strip())
            #
            # if user_id:
            #     user.Client.user_follow(user_id)
            #     print(f"Following {user_id}")
            # else:
            #     print(f"User {user_id} not found")
            return f'사용자: {user.UserName} 팔로우대상: {line.strip()}'
        except LoginRequired:
            user.Client.relogin()  # Use clean session
            # self.insta.UserList[1].Client.dump_settings(file)
            # print('에러: Initialize')
            return f'에러: Initialize'
        except OSError:
            return f'에러: Initialize'
            #print('에러: Initialize')

    def FollowingWork(self):

        try:
            # start_time = time.time()  # 작업 시작 시간 기록

            #팔로우 대상자 추출
            file_path = Config.FollowListPath
            with open(file_path, 'r') as file:
                self.Follow = file.readlines()

            #병렬 작업 등록(풀링)
            #각 작업 대상 id별로 팔로우 작업을 작업 계정에 동시에 등록
            results = []
            with ThreadPoolExecutor() as executor:
                for line in self.Follow:
                    for user in self.insta.UserList:
                        result = executor.submit(self.Follower, user, line)
                        results.append(result)

            for future in results:
                print(future.result())  # 결과 출력
            # for line in self.insta.Follow:
            #
            #     #병렬 처리
            #
            #     self.insta.UserList[1].Client.delay_range = [1, 3]
            #     # print(line.strip())  # 각 줄의 데이터 출력 (strip()으로 공백 제거)
            #     user_id = self.insta.UserList[1].Client.user_id_from_username(line.strip())
            #     if user_id:
            #         self.insta.UserList[1].Client.user_follow(user_id)
            #         print(f"Following {user_id}")
            #     else:
            #         print(f"User {user_id} not found")


            # end_time = time.time()  # 작업 종료 시간 기록
            # elapsed_time = end_time - start_time  # 경과 시간 계산
            # print(f"작업이 완료되었습니다. 소요된 시간: {elapsed_time}초")
        except LoginRequired:
            self.insta.UserList[1].Client.relogin()  # Use clean session
            # self.insta.UserList[1].Client.dump_settings(file)
        except OSError:
            print('에러: Initialize')


    def ReLogin(self,user):
        counter = 2
        while (counter != 0):
            try:
                user_id = bot.user_id_from_username(PROFILE)
                medias = bot.user_medias(user_id)
                break
            except LoginRequired:
                print("Login failed. Relogging in....")
                bot.relogin()
                bot.dump_settings(SESSION_JSON)
                counter = counter - 1

    def Logger(self,user,line):
        try:

            return f'사용자: {user.UserName} 팔로우대상: {line.strip()}'
        except LoginRequired:
            user.Client.relogin()  # Use clean session

            return f'에러: Initialize'
        except OSError:
            return f'에러: Initialize'
            #print('에러: Initialize')

    def ReLoginWork(self):
        try:
            while True:
                pass

        except OSError:
            print('에러: Initialize')