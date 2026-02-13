from dataclasses import dataclass
from typing import Dict


CATALOG: Dict[str, int] = {
    "small_pack": 100,
    "epic_chest": 500,
    "legendary_skin": 1000,
    "battle_pass": 2000,
}


@dataclass(frozen=True)
class PaymentRequest:
    user_id: int
    sku: str
    stars: int
    nonce: str


def build_launch_text(user_name: str) -> str:
    return (
        f"{user_name}, добро пожаловать в Relic Wars!\\n"
        "Открой мини-приложение кнопкой Play и начни охоту за реликвиями."
    )


def validate_precheckout(req: PaymentRequest) -> bool:
    if req.sku not in CATALOG:
        return False
    if CATALOG[req.sku] != req.stars:
        return False
    if len(req.nonce) < 8:
        return False
    return True


def build_fulfillment_payload(req: PaymentRequest, telegram_charge_id: str) -> dict:
    if not validate_precheckout(req):
        raise ValueError("Invalid payment request")
    return {
        "user_id": req.user_id,
        "sku": req.sku,
        "stars": req.stars,
        "telegram_payment_charge_id": telegram_charge_id,
        "status": "confirmed",
    }
