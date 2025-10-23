from typing import List, Optional
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
import logging

logger = logging.getLogger(__name__)


class CustomerService:
    """Customer service"""
    
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository
    
    async def create_customer(self, customer_data: CustomerCreate) -> CustomerResponse:
        """Create customer"""
        try:
            # Check if phone already exists
            existing_customer = await self.customer_repository.get_by_phone(customer_data.phone)
            if existing_customer:
                raise ValueError(f"Customer with phone {customer_data.phone} already exists")
            
            customer = await self.customer_repository.create(customer_data.dict())
            logger.info(f"Customer created: {customer.phone}")
            return CustomerResponse.from_attributes(customer)
            
        except Exception as e:
            logger.error(f"Failed to create customer: {str(e)}")
            raise
    
    async def get_customer(self, customer_id: int) -> Optional[CustomerResponse]:
        """Get customer by ID"""
        customer = await self.customer_repository.get_by_id(customer_id)
        if not customer:
            return None
        
        return CustomerResponse.from_attributes(customer)
    
    async def get_customer_by_phone(self, phone: str) -> Optional[CustomerResponse]:
        """Get customer by phone"""
        customer = await self.customer_repository.get_by_phone(phone)
        if not customer:
            return None
        
        return CustomerResponse.from_attributes(customer)
    
    async def get_all_customers(self) -> List[CustomerResponse]:
        """Get all customers"""
        customers = await self.customer_repository.get_all()
        return [CustomerResponse.from_attributes(customer) for customer in customers]
    
    async def update_customer(self, customer_id: int, customer_data: CustomerUpdate) -> Optional[CustomerResponse]:
        """Update customer"""
        customer = await self.customer_repository.get_by_id(customer_id)
        if not customer:
            return None
        
        try:
            update_data = customer_data.dict(exclude_unset=True)
            
            # Check phone uniqueness if changing
            if 'phone' in update_data and update_data['phone'] != customer.phone:
                existing_customer = await self.customer_repository.get_by_phone(update_data['phone'])
                if existing_customer:
                    raise ValueError(f"Customer with phone {update_data['phone']} already exists")
            
            for key, value in update_data.items():
                setattr(customer, key, value)
            
            updated_customer = await self.customer_repository.update(customer)
            logger.info(f"Customer updated: {updated_customer.phone} (ID: {updated_customer.id})")
            return CustomerResponse.from_attributes(updated_customer)
            
        except Exception as e:
            logger.error(f"Failed to update customer: {str(e)}")
            raise
    
    async def delete_customer(self, customer_id: int) -> bool:
        """Delete customer"""
        try:
            result = await self.customer_repository.delete(customer_id)
            if result:
                logger.info(f"Customer deleted: {customer_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete customer: {str(e)}")
            raise
    
    async def get_or_create_customer(self, phone: str, **kwargs) -> CustomerResponse:
        """Get existing customer or create new one"""
        try:
            # Try to get existing customer
            customer = await self.get_customer_by_phone(phone)
            if customer:
                return customer
            
            # Create new customer
            customer_data = CustomerCreate(phone=phone, **kwargs)
            return await self.create_customer(customer_data)
            
        except Exception as e:
            logger.error(f"Failed to get or create customer: {str(e)}")
            raise
