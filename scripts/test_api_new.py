#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки роботи API з новою логікою
"""

import asyncio
import httpx
import json


async def test_api():
    """Тестування API endpoints з новою логікою"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Тест кореневого endpoint
        print("Testing root endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Тест health check
        print("\nTesting health check...")
        response = await client.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Тест отримання товарів
        print("\n1. Testing products API...")
        response = await client.get(f"{base_url}/api/v1/products/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"Found {len(products)} products")
            if products:
                print(f"First product: {products[0]['name']} - {products[0]['price']} UAH")
        else:
            print(f"Error: {response.text}")
        
        # Тест розрахунку платежу
        print("\n2. Testing payment calculation...")
        products_for_calculation = [
            {"product_id": 1, "quantity": 1},  # Телевизор
            {"product_id": 4, "quantity": 2}   # Навушники
        ]
        
        response = await client.post(
            f"{base_url}/api/v1/payments/calculate",
            json=products_for_calculation
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            calculation = response.json()
            print(f"Total sum: {calculation['total_sum']} UAH")
            print(f"Products: {len(calculation['products'])} items")
        else:
            print(f"Error: {response.text}")
        
        # Тест валідації клієнта
        print("\n3. Testing client validation...")
        test_phone = "+380000000001"
        response = await client.post(
            f"{base_url}/api/v1/payments/validate",
            params={"phone": test_phone}
        )
        print(f"Status: {response.status_code}")
        print(f"Validation result: {response.json()}")
        
        # Тест створення платежу з новою логікою
        print("\n4. Testing payment creation with new logic...")
        
        payment_data = {
            "store_order_id": "test_order_003",
            "client_phone": "+380000000001",
            "invoice": {
                "date": "2024-01-22",
                "number": "INV-003",
                "point_id": 1234,
                "source": "INTERNET"
            },
            "available_programs": [
                {
                    "available_parts_count": [3, 4, 6, 9],
                    "type": "payment_installments"
                }
            ],
            "products": products_for_calculation,
            "result_callback": "https://your-store-domain.com/handle/pay-part/result"
        }
        
        response = await client.post(
            f"{base_url}/api/v1/payments/create",
            json=payment_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            payment_result = response.json()
            print(f"Payment created: ID {payment_result['payment_id']}")
            print(f"External ID: {payment_result['external_id']}")
            print(f"Total sum: {payment_result['total_sum']} UAH")
        else:
            print(f"Error: {response.text}")
        
        # Тест отримання статусу платежу
        if response.status_code == 200:
            payment_result = response.json()
            payment_id = payment_result.get('external_id')
            if payment_id:
                print(f"\n5. Testing payment status...")
                response = await client.get(f"{base_url}/api/v1/payments/{payment_id}/status")
                print(f"Status: {response.status_code}")
                print(f"Payment status: {response.json()}")


if __name__ == "__main__":
    print("Starting API tests with new logic...")
    asyncio.run(test_api())
    print("\nTests completed!")
