from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Product:
    name: str = ""
    merchant_code: str = ""
    quantity: int = 0
    total_price: float = 0.0

    def export(self) -> str:
        return f"{self.name} ({self.merchant_code}) x{self.quantity}: {self.total_price}"


@dataclass(frozen=True, slots=True)
class Order:
    order_code: str
    creation_date: str = ""
    creation_time: str = ""
    issue_date: str = ""
    courier_handover_date: str = ""
    status: str = ""
    state: str = ""
    customer_first_name: str = ""
    customer_last_name: str = ""
    phone: str = ""
    comment: str = ""
    city: str = ""
    warehouse: str = ""
    warehouse_city: str = ""
    delivery_mode: str = ""
    total_price: float = 0.0
    delivery_subsidy_cost: float = 0.0
    delivery_cost: float = 0.0
    products: list[Product] = field(default_factory=list)

    @property
    def product_count(self) -> int:
        return sum(product.quantity for product in self.products)

    def to_row(self) -> dict[str, Any]:
        result = {
            "OrderCode": self.order_code,
            "CreationDate": self.creation_date,
            "CreationTime": self.creation_time,
            "IssueDate": self.issue_date,
            "CourierHandoverDate": self.courier_handover_date,
            "Status": self.status,
            "State": self.state,
            "CustomerFirstName": self.customer_first_name,
            "CustomerLastName": self.customer_last_name,
            "Phone": self.phone,
            "Comment": self.comment,
            "City": self.city,
            "Warehouse": self.warehouse,
            "WarehouseCity": self.warehouse_city,
            "DeliveryMode": self.delivery_mode,
            "TotalPrice": self.total_price,
            "DeliverySubsidyCost": self.delivery_subsidy_cost,
            "DeliveryCost": self.delivery_cost,
            "ProductCount": self.product_count,
        }
        for index, product in enumerate(self.products, start=1):
            result[f"ProductName{index}"] = product.name
            result[f"ProductsArticul{index}"] = product.merchant_code
            result[f"ProductPrice{index}"] = product.total_price
        return result
