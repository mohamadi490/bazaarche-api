from services.payments.base import OnlinePayment, PaymentStrategy, WalletPayment
from sqlalchemy.orm import Session

class PaymentFactory:
    @staticmethod
    def get_strategy(db: Session, payment_code: str) -> PaymentStrategy:
        strategies = {
            "online": OnlinePayment(db),
            "wallet": WalletPayment(db),
        }
        return strategies.get(payment_code)