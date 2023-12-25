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

class User:
    def __init__(self, username, password):
        # 클라이언트 객체
        self.Client = None
        # 세션정보
        self.Session = None
        self.UserName = username
        self.Password = password
        self.LoginYn = 'N'

        # 사용불가여부(3번 정도의 재로그인이 불가능 하다면 폐기 처리 하기 위함)
        self.Disabled = 'N'


class IP:
    def __init__(self, ip, port):
        self.IP = ip
        self.Port = port
