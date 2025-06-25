import pyotp
from workspace.tools.env.config_loader import OTP_SECRET


def generate_otp(secret: str = OTP_SECRET) -> str:
    """
    使用預設 OTP_SECRET 產生 6 位數 OTP 驗證碼。
    如果傳入其他 secret，則使用該值產生。
    """
    return pyotp.TOTP(secret).now()


if __name__ == "__main__":
    print("Current OTP =", generate_otp())
