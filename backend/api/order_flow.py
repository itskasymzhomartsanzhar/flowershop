from typing import Optional, Tuple

from .models import Orders


DELIVERY_FLOW = [
    Orders.StatusEnum.PLACED,
    Orders.StatusEnum.ASSEMBLING_STARTED,
    Orders.StatusEnum.ASSEMBLING_DONE,
    Orders.StatusEnum.COURIER_PICKED,
    Orders.StatusEnum.DELIVERING,
    Orders.StatusEnum.DELIVERED,
]

PICKUP_FLOW = [
    Orders.StatusEnum.PLACED,
    Orders.StatusEnum.ASSEMBLING_STARTED,
    Orders.StatusEnum.ASSEMBLING_DONE,
    Orders.StatusEnum.READY_FOR_PICKUP,
    Orders.StatusEnum.ISSUED,
]

STATUS_LABELS = {
    Orders.StatusEnum.PENDING_PAYMENT: "Ожидает оплаты",
    Orders.StatusEnum.PLACED: "Оформление",
    Orders.StatusEnum.ASSEMBLING_STARTED: "Сборка у флористов (взялись за заказ)",
    Orders.StatusEnum.ASSEMBLING_DONE: "Сборка у флористов (готова)",
    Orders.StatusEnum.COURIER_PICKED: "Курьер забрал (передача)",
    Orders.StatusEnum.DELIVERING: "Доставка",
    Orders.StatusEnum.DELIVERED: "Доставлено",
    Orders.StatusEnum.READY_FOR_PICKUP: "Готов к выдаче",
    Orders.StatusEnum.ISSUED: "Выдан",
    Orders.StatusEnum.PAID: "Оформление",
    Orders.StatusEnum.ASSEMBLING: "Сборка у флористов (взялись за заказ)",
    Orders.StatusEnum.ONTHEWAY: "Доставка",
}

ACTION_LABELS = {
    Orders.StatusEnum.ASSEMBLING_STARTED: "Сборка начата",
    Orders.StatusEnum.ASSEMBLING_DONE: "Сборка готова",
    Orders.StatusEnum.COURIER_PICKED: "Курьер забрал",
    Orders.StatusEnum.DELIVERING: "Доставка",
    Orders.StatusEnum.DELIVERED: "Доставлено",
    Orders.StatusEnum.READY_FOR_PICKUP: "Готов к выдаче",
    Orders.StatusEnum.ISSUED: "Выдан",
}


def normalize_status(status: Optional[str]) -> str:
    if not status:
        return Orders.StatusEnum.PLACED
    return status


def get_next_status(order: Orders) -> Optional[str]:
    current = normalize_status(order.status)
    if current == Orders.StatusEnum.PENDING_PAYMENT:
        return None
    flow = PICKUP_FLOW if order.is_pickup else DELIVERY_FLOW
    if current not in flow:
        return None
    idx = flow.index(current)
    if idx + 1 >= len(flow):
        return None
    return flow[idx + 1]


def get_status_label(status: Optional[str]) -> str:
    status_key = normalize_status(status)
    return STATUS_LABELS.get(status_key, "Оформление")


def build_staff_keyboard(order: Orders) -> Optional[dict]:
    next_status = get_next_status(order)
    if not next_status:
        return None
    label = ACTION_LABELS.get(next_status)
    if not label:
        return None
    callback_data = f"order:{order.id}:{next_status}"
    return {
        "inline_keyboard": [[{"text": label, "callback_data": callback_data}]]
    }
