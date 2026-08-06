from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    creation_time: str = ""
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
    products: list[Product] = field(default_factory=list)

    @property
    def product_count(self) -> int:
        return len(self.products)

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row.pop("products")
        return {
            "OrderCode": self.order_code,
            "CreationTime": self.creation_time,
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
            "ProductCount": self.product_count,
            "Products": "; ".join(product.export() for product in self.products),
        }
