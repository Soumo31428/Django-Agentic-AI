from orders.models import Order, RefundRequest
from django.utils import timezone
from .tracking_data import DELIVERY_DATA

def get_order_details(order_id):
    try:
        order = Order.get(id=order_id)
        return {
            "order_id": order.id,
            "product_name": order.product_name,
            "amount": str(order.amount),
            "status": order.status,
            "carrier": order.carrier,
            "delivery": order.delivery,
            "ordered_on": order.created_at.strftime("%d %b %Y"),  #25 July 2026
            "days_since_order": (timezone.now() - order.created_at).days,
        }

    except Order.DoesNotExist:
        return {"error": f"Order #{order_id} not found"}


def get_refund_history(user_id):
    refunds = RefundRequest.objects.filter(user_id=user_id).order_by("-created_at")
    history = []
    for refund in refunds:
        history.append({
            "order_id": refund.order.id, 
            "product": refund.order.product_name,
            "reason": refund.reason,
            "status": refund.status,
            "requested_on": refund.created_at.strftime("%d %b %Y"),
        })
    return {
        "total_rufund_requests": len(history),
        "history": history,
    }

def check_delivery_status(tracking_namber, carrier):
    default_response = {
        "status": "Unknown",
        "last_location": "Tracking info unavailable",
        "last_update": "N/A",
        "estimated_delivery": "Contact carrier directly",
        "delay_reason": "No updates from carrier",
    } 
    result = DELIVERY_DATA.get(tracking_namber, default_response)
    result["tracking_number"] = tracking_namber
    result["carrirer"] = carrier
    return result
