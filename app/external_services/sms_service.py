from kavenegar import *

def send_sms(phone_number: str, code: str):
    try:
        api = KavenegarAPI('3661596A78414535756C6D4C307179395334707A436A486E7A5861345A5343452F5369566363336B4758633D')
        params = {
        'receptor': phone_number,
        'token': code,
        'template': 'verificationCode',
        'type': 'sms'
        }
        response = api.verify_lookup(params)
        print(response)
        return True
    except APIException as e:
        print(str(e))
        return False
    except HTTPException as e:
        print(str(e))
        return False