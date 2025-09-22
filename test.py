import hashlib
import hmac
import base64
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any


class MonobankAPI:
    """
    Клас для роботи з API Monobank "Покупка Частинами"
    """
    
    def __init__(self, store_id: str, store_secret: str, base_url: str = "https://u2-demo-ext.mono.st4g3.com"):
        """
        Ініціалізація API клієнта
        
        Args:
            store_id: ID магазину
            store_secret: Секретний ключ для підпису
            base_url: Базовий URL API
        """
        self.store_id = store_id
        self.store_secret = store_secret
        self.base_url = base_url.rstrip('/')
        
    def _generate_signature(self, request_body: str) -> str:
        """
        Генерація HMAC-SHA256 підпису для запиту
        
        Args:
            request_body: Тіло запиту у JSON форматі
            
        Returns:
            Base64 закодований підпис
        """
        message_bytes = request_body.encode('utf-8')
        key_bytes = self.store_secret.encode('utf-8')
        
        signature = hmac.new(
            key_bytes,
            message_bytes,
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _make_request(self, endpoint: str, data: Dict[str, Any], method: str = "POST") -> Dict[str, Any]:
        """
        Виконання HTTP запиту до API
        
        Args:
            endpoint: Кінець URL для запиту
            data: Дані для відправки
            method: HTTP метод (GET, POST, PUT)
            
        Returns:
            Відповідь від API у форматі JSON
        """
        url = f"{self.base_url}{endpoint}"
        request_body = json.dumps(data, ensure_ascii=False)
        signature = self._generate_signature(request_body)
        
        headers = {
            'store-id': self.store_id,
            'signature': signature,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, data=request_body, headers=headers)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def validate_client(self, phone: str) -> Dict[str, Any]:
        """
        Валідація клієнта за номером телефону
        
        Args:
            phone: Номер телефону клієнта
            
        Returns:
            Результат валідації від API
        """
        data = {"phone": phone}
        return self._make_request("/api/client/validate", data)
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Створення замовлення на покупку частинами
        
        Args:
            order_data: Дані замовлення
            
        Returns:
            Результат створення замовлення
        """
        return self._make_request("/api/order/create", order_data)
    
    def confirm_store(self, order_id: str, confirmed: bool = True) -> Dict[str, Any]:
        """
        Підтвердження магазином видачі товару
        
        Args:
            order_id: ID замовлення
            confirmed: Чи підтверджується видача товару
            
        Returns:
            Результат підтвердження
        """
        data = {
            "order_id": order_id,
            "confirmed": confirmed
        }
        return self._make_request("/api/order/confirm", data)
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Отримання статусу замовлення
        
        Args:
            order_id: ID замовлення
            
        Returns:
            Статус замовлення
        """
        return self._make_request(f"/api/order/{order_id}/status", {}, "GET")


def create_test_order_data(phone: str, total_sum: float, products: List[Dict]) -> Dict[str, Any]:
    """
    Створення тестових даних замовлення
    
    Args:
        phone: Номер телефону клієнта
        total_sum: Загальна сума замовлення
        products: Список товарів
        
    Returns:
        Дані замовлення для API
    """
    return {
        "store_order_id": f"test_order_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "client_phone": phone,
        "total_sum": total_sum,
        "invoice": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "number": f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "point_id": 1234,
            "source": "INTERNET"
        },
        "available_programs": [
            {
                "available_parts_count": [3, 4, 6, 9],
                "type": "payment_installments"
            }
        ],
        "products": products,
        "result_callback": "https://your-store-domain.com/handle/pay-part/result"
    }


def handle_callback(callback_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обробка callback від банку
    
    Args:
        callback_data: Дані callback від банку
        
    Returns:
        Результат обробки callback
    """
    order_id = callback_data.get("order_id")
    status = callback_data.get("status")
    
    print(f"Received callback for order {order_id} with status: {status}")
    
    if status == "APPROVED":
        print("Order approved by client")
        return {"processed": True, "action": "print_receipt"}
    elif status == "REJECTED":
        print("Order rejected by client")
        return {"processed": True, "action": "cancel_order"}
    elif status == "WAITING_FOR_STORE_CONFIRM":
        print("Order waiting for store confirmation")
        return {"processed": True, "action": "wait_for_store_confirm"}
    
    return {"processed": False, "error": "Unknown status"}


def main():
    """
    Основна функція з прикладами використання
    """
    # Тестові креденціали
    STORE_ID = "test_store_with_confirm"
    STORE_SECRET = "secret_98765432--123-123"
    
    # Ініціалізація API клієнта
    api = MonobankAPI(STORE_ID, STORE_SECRET)
    
    print("=== Monobank API Test ===")
    
    # Тест 1: Валідація клієнта
    print("\n1. Testing client validation...")
    test_phones = ["+380000000001", "+380000000002", "+380000000003"]
    
    for phone in test_phones:
        result = api.validate_client(phone)
        print(f"Phone {phone}: {result}")
    
    # Тест 2: Створення замовлення
    print("\n2. Testing order creation...")
    
    products = [
        {
            "name": "Телевизор Samsung",
            "count": 1,
            "sum": 15000.00
        },
        {
            "name": "Навушники",
            "count": 2,
            "sum": 2500.00
        }
    ]
    
    order_data = create_test_order_data("+380000000001", 17500.00, products)
    order_result = api.create_order(order_data)
    print(f"Order creation result: {order_result}")
    
    # Тест 3: Отримання статусу замовлення
    if "order_id" in order_result:
        print("\n3. Testing order status...")
        order_id = order_result["order_id"]
        status_result = api.get_order_status(order_id)
        print(f"Order status: {status_result}")
    
    # Тест 4: Симуляція callback
    print("\n4. Testing callback handling...")
    
    test_callbacks = [
        {"order_id": "test_order_123", "status": "APPROVED"},
        {"order_id": "test_order_124", "status": "REJECTED"},
        {"order_id": "test_order_125", "status": "WAITING_FOR_STORE_CONFIRM"}
    ]
    
    for callback in test_callbacks:
        result = handle_callback(callback)
        print(f"Callback {callback['status']}: {result}")
    
    # Тест 5: Підтвердження магазину
    print("\n5. Testing store confirmation...")
    confirm_result = api.confirm_store("test_order_123", True)
    print(f"Store confirmation result: {confirm_result}")


if __name__ == "__main__":
    main()
