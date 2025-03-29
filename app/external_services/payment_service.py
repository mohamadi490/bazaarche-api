from models.enums.transaction_enums import TransactionStatus
from schemas.transaction import VerifyTransaction, PayTransactionRes, VerifyTransactionRes
from fastapi import HTTPException
import requests

ZARINPAL_SANDBOX = "https://sandbox.zarinpal.com/pg/v4/payment/"
MERCHANT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

class Payment:
    
    def request_pay(self, amount: int, description: str) -> PayTransactionRes:
        try:
            # get callback_url from setting
            callback_url = "http://127.0.0.1:4200/verify"
            response = requests.post(
                f"{ZARINPAL_SANDBOX}request.json",
                json={
                    "merchant_id": MERCHANT_ID,
                    "amount": amount,
                    "callback_url": callback_url,
                    "description": description,
                }
            )
            res_data = response.json()
            
            if res_data['data']["code"] != 100:
                raise HTTPException(status_code=500, detail="payment Error!")
            return PayTransactionRes(
                status_code=res_data['data']["code"],
                payment_url=f"https://sandbox.zarinpal.com/pg/StartPay/{res_data['data']['authority']}",
                res_number=res_data['data']['authority']
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="payment Error!")

    def verify_pay(self, data: VerifyTransaction) -> VerifyTransactionRes:
        if data.status != "OK":
            return VerifyTransactionRes(status=TransactionStatus.Canceled)
        
        try:
            response = requests.post(
                f"{ZARINPAL_SANDBOX}verify.json",
                json={
                    "merchant_id": MERCHANT_ID,
                    "authority": data.res_number,
                    "amount": data.amount,
                }
            )
            res_data = response.json()
            code = res_data['data'].get("code", None)  # Safely get the code
            
            if code is None:
                raise HTTPException(status_code=500, detail="Invalid response structure")
            
            status = TransactionStatus.Success if code == 100 else TransactionStatus.Failed
            return VerifyTransactionRes(
                status=status,
                ref_id=res_data.get("RefID", None),
                fee=res_data.get("fee", None),
                fee_type=res_data.get("fee_type", None),
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="Payment verification error!")