from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from core.database import get_db
from models.order import Order
from apscheduler.schedulers.background import BackgroundScheduler

def delete_pending_orders_older_than_one_hour(db: Session):
    one_hour_ago = datetime.now() - timedelta(hours=1)
    pending_orders = db.query(Order).filter(
        Order.status == "pending",
        Order.created_at < one_hour_ago
    ).all()

    for order in pending_orders:
        db.delete(order)

    db.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(delete_pending_orders_older_than_one_hour, 'interval', hours=1, args=[get_db()])
scheduler.start()
        