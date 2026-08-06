from __future__ import annotations

from typing import Any

from models import Order, Product
from utils import deep_get, safe_float, safe_int


class OrderParser:
    def parse(self, payload: dict[str, Any], fallback_order_code: str) -> Order:
        detail = deep_get(payload, "data.merchant.orderDetail", {})
        if not isinstance(detail, dict):
            raise ValueError(f"Missing orderDetail for order {fallback_order_code}")
        products = [self._parse_product(entry) for entry in detail.get("entries") or []]
        return Order(
            order_code=str(detail.get("code") or fallback_order_code),
            creation_time=str(detail.get("creationTime") or ""),
            status=str(detail.get("status") or ""),
            state=str(detail.get("state") or ""),
            customer_first_name=str(deep_get(detail, "customer.firstName", "")),
            customer_last_name=str(deep_get(detail, "customer.lastName", "")),
            phone=str(deep_get(detail, "customer.phoneNumber", "")),
            comment=str(detail.get("commentText") or ""),
            city=str(deep_get(detail, "destination.city.name", "")),
            warehouse=str(deep_get(detail, "warehouse.name", "")),
            warehouse_city=str(deep_get(detail, "warehouse.city.name", "")),
            delivery_mode=str(deep_get(detail, "delivery.mode", "")),
            total_price=safe_float(detail.get("totalPrice")),
            products=products,
        )

    def _parse_product(self, entry: dict[str, Any]) -> Product:
        return Product(
            name=str(deep_get(entry, "product.name", "")),
            merchant_code=str(deep_get(entry, "merchantProduct.code", "")),
            quantity=safe_int(entry.get("quantity")),
            total_price=safe_float(entry.get("totalPrice")),
        )


if __name__ == "__main__":
    from app import main

    raise SystemExit(main())
