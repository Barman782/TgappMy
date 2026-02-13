from bot_service.bot.core import (
    PaymentRequest,
    build_fulfillment_payload,
    build_launch_text,
    validate_precheckout,
)


def test_launch_text_contains_name_and_prompt():
    text = build_launch_text("Seo")
    assert "Seo" in text
    assert "мини-приложение" in text


def test_validate_precheckout_ok():
    req = PaymentRequest(user_id=1, sku="small_pack", stars=100, nonce="abcdefgh")
    assert validate_precheckout(req)


def test_validate_precheckout_fails_wrong_amount():
    req = PaymentRequest(user_id=1, sku="small_pack", stars=999, nonce="abcdefgh")
    assert not validate_precheckout(req)


def test_build_fulfillment_payload():
    req = PaymentRequest(user_id=42, sku="epic_chest", stars=500, nonce="abcdefgh")
    payload = build_fulfillment_payload(req, telegram_charge_id="tg_123")
    assert payload["status"] == "confirmed"
    assert payload["telegram_payment_charge_id"] == "tg_123"
