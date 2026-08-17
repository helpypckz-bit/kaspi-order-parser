from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from models import Order, Product
from utils import deep_get, safe_float, safe_int


class OrderParser:
    def parse(self, payload: dict[str, Any], fallback_order_code: str) -> Order:
        detail = deep_get(payload, "data.merchant.orderDetail", {})
        if not isinstance(detail, dict):
            raise ValueError(f"Missing orderDetail for order {fallback_order_code}")
    
        products = [self._parse_product(entry) for entry in detail.get("entries") or []]
    
        creation_date, creation_time = self._format_datetime(detail.get("creationTime"))
        issue_date, _ = self._format_datetime(deep_get(detail, "delivery.actualDeliveryDate", ""))
        courier_handover_date, _ = self._format_datetime(
            self._order_step_actual_time(detail, "TRANSMISSION")
        )
    
        return Order(
            order_code=str(detail.get("code") or fallback_order_code),
            creation_date=creation_date,
            creation_time=creation_time,
            issue_date=issue_date,
            courier_handover_date=courier_handover_date,
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
            delivery_subsidy_cost=safe_float(detail.get("deliverySubsidyCost")),
            delivery_cost=safe_float(detail.get("deliveryCost")),
            products=products,
        )

    def _format_datetime(self, value: Any) -> tuple[str, str]:
        if not value:
            return "", ""
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return str(value), ""
        local_dt = dt.astimezone(ZoneInfo("Asia/Almaty"))
        return local_dt.strftime("%d.%m.%Y"), local_dt.strftime("%H:%M:%S")

    def _order_step_actual_time(self, detail: dict[str, Any], step_name: str) -> Any:
        for order_step in detail.get("orderSteps") or []:
            if order_step.get("step") == step_name:
                return order_step.get("actualTime")
        return None

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
