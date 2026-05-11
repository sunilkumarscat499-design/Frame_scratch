from utils.test_api_token import APIUtils

def test_get_order_id(get_token):
    obj = APIUtils()
    print(get_token)
    response = obj.create_order(get_token)
    assert response.ok # this will check if status 200-299
    assert response.status == 201 #to check if code is specific
    json_response = response.json()
    print(json_response)
    assert "orders"in json_response
    assert json_response.get("message") == "Order Placed Successfully"

