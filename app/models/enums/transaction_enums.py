from enum import Enum


class TransactionType(Enum):
    order = "order"
    wallet_deposit = "wallet_deposit"
    wallet_withdraw = "wallet_withdraw"


class TransactionStatus(Enum):
    Success = "success"
    Failed = "failed"
    Canceled = "canceled"
    Pending = "pending"