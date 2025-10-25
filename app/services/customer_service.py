from typing import List, Optional
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.crm_service import CRMService
import logging

logger = logging.getLogger(__name__)


class CustomerService:
    """Customer service"""
    
    def __init__(self, customer_repository: CustomerRepository, crm_service: CRMService = None):
        self.customer_repository = customer_repository
        self.crm_service = crm_service
    
    async def ensure_customer(self, customer_data: CustomerCreate) -> CustomerResponse:
        """Create customer with optional CRM integration or return existing customer"""
        try:
            # Check if phone already exists
            existing_customer = await self.customer_repository.get_by_phone(customer_data.phone)
            if existing_customer:
                logger.info(f"Customer with phone {customer_data.phone} already exists, returning existing")
            
            # Validate Bitrix ID if provided
            if customer_data.bitrix_id and self.crm_service:
                is_valid = await self.crm_service.validate_contact_id_by_phone(
                    customer_data.bitrix_id, customer_data.phone
                )
                if not is_valid:
                    raise ValueError(f"Bitrix ID {customer_data.bitrix_id} doesn't match phone {customer_data.phone}")
            
            # Create customer in database
            if not existing_customer:
                customer = await self.customer_repository.create(customer_data.dict())
            else:
                customer = existing_customer
            
            # Create CRM contact if no Bitrix ID provided
            if not customer_data.bitrix_id and self.crm_service and not customer.bitrix_id:
                try:
                    crm_result = await self.crm_service.create_contact_from_customer(customer_data)
                    if crm_result.get("result"):
                        customer.bitrix_id = str(crm_result["result"])
                        await self.customer_repository.update(customer)
                        logger.info(f"CRM contact created for customer: {customer.phone}")
                except Exception as crm_error:
                    logger.warning(f"Failed to create CRM contact: {str(crm_error)}")
            
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
            # Create new customer if not exists or return existing user
            customer_data = CustomerCreate(phone=phone, **kwargs)
            return await self.ensure_customer(customer_data)
            
        except Exception as e:
            logger.error(f"Failed to get or create customer: {str(e)}")
            raise
