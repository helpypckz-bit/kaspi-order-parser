from parser import OrderParser


def test_parse_order_detail() -> None:
    payload = {
        "data": {"merchant": {"orderDetail": {
            "code": "1022135385",
            "creationTime": "2026-01-01T00:00:00Z",
            "status": "APPROVED",
            "state": "NEW",
            "commentText": "comment",
            "totalPrice": 1000,
            "deliverySubsidyCost": 300,
            "deliveryCost": 500,
            "customer": {"firstName": "A", "lastName": "B", "phoneNumber": "+7"},
            "delivery": {"mode": "DELIVERY", "actualDeliveryDate": "2026-01-03T00:00:00Z"},
            "orderSteps": [
                {"step": "TRANSMISSION", "actualTime": "2026-01-02T00:00:00Z"}
            ],
            "destination": {"city": {"name": "Almaty"}},
            "warehouse": {"name": "Main", "city": {"name": "Almaty"}},
            "entries": [
                {
                    "quantity": 2,
                    "totalPrice": 1000,
                    "product": {"name": "Phone"},
                    "merchantProduct": {"code": "SKU1"},
                },
                {
                    "quantity": 3,
                    "totalPrice": 600,
                    "product": {"name": "Case"},
                    "merchantProduct": {"code": "SKU2"},
                },
            ],
        }}}
    }
    order = OrderParser().parse(payload, "fallback")
    assert order.order_code == "1022135385"
    assert order.creation_date == "01.01.2026"
    assert order.creation_time == "05:00:00"
    assert order.issue_date == "03.01.2026"
    assert order.courier_handover_date == "02.01.2026"
    assert order.delivery_subsidy_cost == 300
    assert order.delivery_cost == 500
    assert order.product_count == 5
    assert order.products[0].merchant_code == "SKU1"
    row = order.to_row()
    assert row["ProductName1"] == "Phone"
    assert row["ProductsArticul1"] == "SKU1"
    assert row["ProductPrice1"] == 1000
    assert row["ProductName2"] == "Case"
    assert row["ProductsArticul2"] == "SKU2"
    assert row["ProductPrice2"] == 600
    assert "Products" not in row
