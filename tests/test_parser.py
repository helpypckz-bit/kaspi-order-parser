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
            "customer": {"firstName": "A", "lastName": "B", "phoneNumber": "+7"},
            "delivery": {"mode": "DELIVERY"},
            "destination": {"city": {"name": "Almaty"}},
            "warehouse": {"name": "Main", "city": {"name": "Almaty"}},
            "entries": [{
                "quantity": 2,
                "totalPrice": 1000,
                "product": {"name": "Phone"},
                "merchantProduct": {"code": "SKU1"},
            }],
        }}}
    }
    order = OrderParser().parse(payload, "fallback")
    assert order.order_code == "1022135385"
    assert order.product_count == 1
    assert order.products[0].merchant_code == "SKU1"
