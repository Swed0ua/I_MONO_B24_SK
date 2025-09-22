#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки роботи API
"""

import asyncio
import httpx
import json


async def test_api():
    """Тестування API endpoints"""
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
        
        # Тест валідації клієнта
        print("\nTesting client validation...")
        test_phone = "+380000000001"
        response = await client.post(
            f"{base_url}/api/v1/payments/validate",
            params={"phone": test_phone}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Тест створення платежу
        print("\nTesting payment creation...")
        payment_data = {
            "store_order_id": "test_order_001",
            "client_phone": "+380000000001",
            "total_sum": 15000.00,
            "invoice": {
                "date": "2024-01-22",
                "number": "INV-001",
                "point_id": 1234,
                "source": "INTERNET"
            },
            "available_programs": [
                {
                    "available_parts_count": [3, 4, 6, 9],
                    "type": "payment_installments"
                }
            ],
            "products": [
                {
                    "name": "Телевизор Samsung",
                    "count": 1,
                    "sum": 15000.00
                }
            ],
            "result_callback": "https://your-store-domain.com/handle/pay-part/result"
        }
        
        response = await client.post(
            f"{base_url}/api/v1/payments/create",
            json=payment_data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")


if __name__ == "__main__":
    print("Starting API tests...")
    asyncio.run(test_api())
    print("\nTests completed!")
