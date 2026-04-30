"""
FASTAPI TUTORIAL 2: DATA MODELS & VALIDATION - DETAILED EXPLANATION
==================================================================

🎯 OBJECTIVE: Master Pydantic data models and understand how FastAPI validates data.

📚 WHAT YOU'LL LEARN:
- How Pydantic BaseModel works internally
- Request body validation and parsing
- Field constraints and validation rules
- Automatic error responses
- Response models and serialization
- Nested models and complex data structures

🚀 RUN THIS TUTORIAL:
    python -m uvicorn tutorial_2_data_models:app --reload

Visit: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import json

app = FastAPI(
    title="FastAPI Data Models Tutorial",
    description="Mastering Pydantic models and validation",
    version="2.0.0"
)

# ============================================================================
# SECTION 1: BASIC PYDANTIC MODELS
# ============================================================================

class User(BaseModel):
    """
    Basic Pydantic model for User data.

    WHAT THIS DOES:
    - Defines the structure of User data
    - Validates incoming data automatically
    - Converts data types (string "123" → int 123)
    - Provides default values for optional fields

    HOW IT WORKS INTERNALLY:
    1. FastAPI receives JSON: {"name": "John", "age": "30", "email": "john@example.com"}
    2. Pydantic validates each field according to type hints
    3. Converts "30" (string) to 30 (integer) automatically
    4. Creates User object with validated data
    5. Passes User object to your function
    """
    name: str           # Required string field
    email: str          # Required string field
    age: int           # Required integer field
    is_active: bool = True  # Optional with default value

@app.post("/users")
def create_user(user: User):
    """
    Create a user with automatic validation.

    WHAT HAPPENS WHEN YOU CALL THIS:

    ✅ VALID REQUEST:
    POST /users
    Content-Type: application/json
    {"name": "John", "email": "john@example.com", "age": 30}

    1. FastAPI parses JSON body
    2. Validates against User model
    3. Converts types (age string → int)
    4. Calls function with User object
    5. Returns success response

    ❌ INVALID REQUEST:
    POST /users
    {"name": "John", "email": "john", "age": "thirty"}

    1. Pydantic validation fails
    2. FastAPI returns 422 error automatically
    3. No code execution in your function
    """
    return {
        "message": "User created successfully",
        "user": user,                    # User object (Pydantic model)
        "user_dict": user.dict(),        # Convert to dictionary
        "user_json": user.json(),        # Convert to JSON string
        "validation_passed": True
    }

"""
PYDANTIC MODEL INTERNALS:

When you define: class User(BaseModel):
    name: str
    age: int

Pydantic creates:
1. __init__ method that validates data
2. Field validators for each attribute
3. Type conversion logic
4. Error message generation
5. Serialization methods (.dict(), .json())

The User object has:
- user.name → "John"
- user.age → 30
- user.dict() → {"name": "John", "age": 30}
- user.json() → '{"name": "John", "age": 30}'
"""

# ============================================================================
# SECTION 2: FIELD CONSTRAINTS & VALIDATION RULES
# ============================================================================

class Product(BaseModel):
    """
    Product model with detailed field constraints.

    Field() allows advanced validation rules:
    - min_length, max_length: String length limits
    - ge, le: Greater/Less than or equal (>=, <=)
    - gt, lt: Greater/Less than (>, <)
    - regex: Pattern matching
    - description: Documentation for API docs
    """
    name: str = Field(
        ...,                           # ... means required (no default)
        min_length=1,                  # Must be at least 1 character
        max_length=100,                # Must be at most 100 characters
        description="Product name"     # Shows in API documentation
    )

    price: float = Field(
        ...,                          # Required
        gt=0,                         # Must be greater than 0
        description="Price in USD"    # API documentation
    )

    quantity: int = Field(
        default=1,                    # Default value if not provided
        ge=0,                         # Greater than or equal to 0
        le=1000,                      # Less than or equal to 1000
        description="Stock quantity (0-1000)"
    )

    category: str = Field(
        ...,                          # Required
        min_length=2,                 # At least 2 characters
        max_length=50,                # At most 50 characters
        description="Product category"
    )

    description: Optional[str] = Field(
        None,                         # Optional field (can be None)
        max_length=500,               # If provided, max 500 chars
        description="Optional product description"
    )

@app.post("/products")
def create_product(product: Product):
    """
    Create product with comprehensive validation.

    TRY THESE REQUESTS:

    ✅ VALID REQUEST:
    {
        "name": "Laptop",
        "price": 999.99,
        "quantity": 10,
        "category": "electronics",
        "description": "High-performance laptop"
    }

    ❌ INVALID - PRICE NEGATIVE:
    {
        "name": "Laptop",
        "price": -100,
        "quantity": 10,
        "category": "electronics"
    }
    → Returns 422: "ensure this value is greater than 0"

    ❌ INVALID - NAME TOO LONG:
    {
        "name": "This is a very very very very very very very very very very long product name that exceeds the maximum length limit of 100 characters",
        "price": 999.99,
        "quantity": 10,
        "category": "electronics"
    }
    → Returns 422: "ensure this value has at most 100 characters"

    ❌ INVALID - QUANTITY TOO HIGH:
    {
        "name": "Laptop",
        "price": 999.99,
        "quantity": 1500,
        "category": "electronics"
    }
    → Returns 422: "ensure this value is less than or equal to 1000"
    """
    return {
        "message": "Product created successfully",
        "product": product,
        "validation_details": {
            "name_length": len(product.name),
            "price_positive": product.price > 0,
            "quantity_in_range": 0 <= product.quantity <= 1000,
            "category_valid": len(product.category) >= 2
        }
    }

"""
FIELD CONSTRAINTS CHEAT SHEET:

STRING CONSTRAINTS:
- min_length=5        → Must be at least 5 characters
- max_length=100      → Must be at most 100 characters
- regex=r"^\d+$"      → Must match regex pattern

NUMERIC CONSTRAINTS:
- gt=0                → Must be greater than 0
- ge=0                → Must be greater than or equal to 0
- lt=100              → Must be less than 100
- le=100              → Must be less than or equal to 100

OTHER CONSTRAINTS:
- multiple_of=5       → Must be multiple of 5
- description="..."   → Documentation text
"""

# ============================================================================
# SECTION 3: CUSTOM VALIDATORS
# ============================================================================

class EmailUser(BaseModel):
    """
    User model with custom validation logic.

    @validator decorators allow custom validation functions.
    """
    name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., description="Valid email address")
    age: int = Field(..., ge=13, le=120, description="Age 13-120")

    @validator('email')
    def email_must_be_valid(cls, v):
        """
        Custom validator for email field.

        This function runs after Pydantic's basic validation.
        You can add any custom logic here.

        Parameters:
        - cls: The model class
        - v: The field value to validate

        Returns: The validated value (possibly modified)
        Raises: ValueError if validation fails
        """
        if '@' not in v:
            raise ValueError('Email must contain @ symbol')

        if not v.endswith(('.com', '.org', '.net', '.edu')):
            raise ValueError('Email must end with .com, .org, .net, or .edu')

        return v.lower()  # Convert to lowercase

    @validator('name')
    def name_must_not_contain_numbers(cls, v):
        """Custom validator to ensure name doesn't contain numbers."""
        if any(char.isdigit() for char in v):
            raise ValueError('Name cannot contain numbers')
        return v.strip()  # Remove leading/trailing whitespace

@app.post("/email-users")
def create_email_user(user: EmailUser):
    """
    Create user with custom validation.

    TRY THESE:

    ✅ VALID:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }

    ❌ INVALID EMAIL (no @):
    {
        "name": "John Doe",
        "email": "john-example.com",
        "age": 30
    }
    → "Email must contain @ symbol"

    ❌ INVALID EMAIL (wrong domain):
    {
        "name": "John Doe",
        "email": "john@example.xyz",
        "age": 30
    }
    → "Email must end with .com, .org, .net, or .edu"

    ❌ INVALID NAME (has numbers):
    {
        "name": "John123",
        "email": "john@example.com",
        "age": 30
    }
    → "Name cannot contain numbers"
    """
    return {
        "message": "Email user created",
        "user": user,
        "custom_validation_passed": True,
        "email_normalized": user.email  # Shows lowercase conversion
    }

"""
VALIDATOR INTERNALS:

@validator('field_name')
def validate_field(cls, v):
    # Your custom logic here
    return v

WHEN VALIDATORS RUN:
1. Pydantic does basic type validation
2. Field constraints are checked (min_length, gt, etc.)
3. Custom validators run in order
4. If any validator raises ValueError, validation fails
5. FastAPI returns 422 error with validator message

VALIDATOR USE CASES:
- Business logic validation
- Data normalization (lowercase, strip whitespace)
- Cross-field validation
- External service validation (check if email exists)
"""

# ============================================================================
# SECTION 4: NESTED MODELS (COMPLEX DATA STRUCTURES)
# ============================================================================

class Address(BaseModel):
    """Address sub-model"""
    street: str
    city: str
    state: str = Field(..., min_length=2, max_length=2, description="2-letter state code")
    zip_code: str = Field(..., pattern=r'^\d{5}(-\d{4})?$', description="ZIP code (12345 or 12345-6789)")
    country: str = "USA"

class OrderItem(BaseModel):
    """Order item sub-model"""
    product_id: int
    quantity: int = Field(..., gt=0, description="Must order at least 1 item")
    price: float = Field(..., ge=0, description="Price cannot be negative")
    product_name: str  # For display purposes

class Order(BaseModel):
    """
    Complex Order model with nested objects.

    This demonstrates:
    - Nested Address object
    - List of OrderItem objects
    - Cross-validation between fields
    """
    customer_id: int
    customer_name: str
    shipping_address: Address          # Nested Address object
    billing_address: Optional[Address] = None  # Optional nested object
    items: List[OrderItem]            # List of OrderItem objects
    total_amount: float = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(credit_card|debit_card|paypal)$")
    order_date: Optional[datetime] = None

    @validator('total_amount')
    def validate_total_matches_items(cls, v, values):
        """
        Cross-field validator: Ensure total matches sum of item prices.

        This validator can access other fields using the 'values' parameter.
        """
        if 'items' in values and values['items']:
            calculated_total = sum(item.quantity * item.price for item in values['items'])
            if abs(v - calculated_total) > 0.01:  # Allow small rounding differences
                raise ValueError(f'Total amount ${v} does not match calculated total ${calculated_total}')
        return v

@app.post("/orders")
def create_order(order: Order):
    """
    Create complex order with nested validation.

    EXAMPLE REQUEST BODY:
    {
        "customer_id": 123,
        "customer_name": "John Doe",
        "shipping_address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345"
        },
        "items": [
            {
                "product_id": 101,
                "quantity": 2,
                "price": 29.99,
                "product_name": "Wireless Mouse"
            },
            {
                "product_id": 102,
                "quantity": 1,
                "price": 999.99,
                "product_name": "Laptop"
            }
        ],
        "total_amount": 1059.97,
        "payment_method": "credit_card"
    }

    WHAT GETS VALIDATED:
    ✅ Address format and ZIP code pattern
    ✅ Order items have positive quantities and prices
    ✅ Payment method is valid option
    ✅ Total amount matches sum of (quantity × price)
    ✅ All nested objects are properly structured
    """
    # Add order date if not provided
    if order.order_date is None:
        order.order_date = datetime.now()

    # Calculate item count for response
    total_items = sum(item.quantity for item in order.items)

    return {
        "message": "Order created successfully",
        "order": order,
        "summary": {
            "customer": order.customer_name,
            "total_items": total_items,
            "total_amount": order.total_amount,
            "payment_method": order.payment_method,
            "shipping_to": f"{order.shipping_address.city}, {order.shipping_address.state}"
        }
    }

"""
NESTED MODEL INTERNALS:

When FastAPI processes nested models:

1. Receives JSON with nested objects
2. Recursively validates each nested model
3. Converts types in nested objects
4. Runs validators on nested models
5. Creates nested Pydantic objects

For Order model:
- order.shipping_address → Address object
- order.items → List[OrderItem] objects
- order.items[0].price → Validated float
"""

# ============================================================================
# SECTION 5: RESPONSE MODELS
# ============================================================================

class UserResponse(BaseModel):
    """Response model for user data"""
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_response(user_id: int):
    """
    Get user with response model.

    response_model tells FastAPI:
    1. Validate the return data against this model
    2. Only include fields defined in the model
    3. Generate API documentation with correct schema
    4. Filter out sensitive fields automatically

    BENEFITS:
    - API consumers know exactly what to expect
    - Sensitive data is automatically excluded
    - Documentation is accurate
    - Type safety for API responses
    """
    if user_id == 999:
        # Simulate not found
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Simulate database lookup
    user_data = {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "is_active": user_id % 2 == 0,  # Even IDs are active
        "created_at": datetime.now(),
        "password_hash": "secret123",  # This will be filtered out!
        "internal_notes": "VIP customer"  # This will be filtered out!
    }

    # Convert to response model (filters out sensitive fields)
    response = UserResponse(**user_data)

    return response

"""
RESPONSE MODEL VS INPUT MODEL:

Input Model (User):         Response Model (UserResponse):
- name: str                 - id: int
- email: str               - name: str
- age: int                 - email: str
- password: str            - is_active: bool
- ...                      - created_at: datetime

Response models ensure:
- Sensitive data (passwords) is never sent to clients
- API contract is clear and documented
- Frontend knows exactly what to expect
"""

# ============================================================================
# SECTION 6: ERROR HANDLING WITH MODELS
# ============================================================================

@app.exception_handler(ValueError)
def value_error_handler(request, exc: ValueError):
    """
    Custom exception handler for validation errors.

    When Pydantic validation fails, FastAPI raises ValueError.
    This handler converts it to a structured JSON response.
    """
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message=str(exc),
            details={"request_url": str(request.url)},
            timestamp=datetime.now()
        ).dict()
    )

@app.post("/validate-test")
def test_validation(product: Product):
    """
    Test validation with custom error responses.

    Try sending invalid data to see structured error responses.
    """
    return {
        "message": "Validation passed!",
        "product": product
    }

# ============================================================================
# SECTION 7: OPTIONAL FIELDS & DEFAULTS
# ============================================================================

class Profile(BaseModel):
    """
    Profile with various field types and defaults.
    """
    username: str
    bio: Optional[str] = None                    # Can be null
    website: Optional[str] = None               # Can be null
    age: Optional[int] = None                   # Can be null
    is_public: bool = True                      # Default true
    theme: str = Field(default="light", pattern="^(light|dark)$")  # Default with validation
    tags: List[str] = Field(default_factory=list)  # Default empty list
    metadata: dict = Field(default_factory=dict)   # Default empty dict

@app.post("/profiles")
def create_profile(profile: Profile):
    """
    Create profile demonstrating optional fields and defaults.

    MINIMAL REQUEST (uses all defaults):
    {
        "username": "johndoe"
    }

    FULL REQUEST (overrides defaults):
    {
        "username": "johndoe",
        "bio": "Software developer",
        "website": "https://example.com",
        "age": 30,
        "is_public": false,
        "theme": "dark",
        "tags": ["python", "fastapi"],
        "metadata": {"level": "expert"}
    }
    """
    return {
        "message": "Profile created",
        "profile": profile,
        "fields_provided": {
            "has_bio": profile.bio is not None,
            "has_website": profile.website is not None,
            "has_age": profile.age is not None,
            "tags_count": len(profile.tags),
            "metadata_keys": list(profile.metadata.keys())
        }
    }

"""
OPTIONAL FIELDS PATTERNS:

1. Optional[str] = None           → Can be omitted or set to null
2. bool = True                    → Has default, always present
3. str = Field(default="value")   → Default with validation
4. List[str] = Field(default_factory=list)    → Default empty list
5. dict = Field(default_factory=dict)         → Default empty dict

KEY DIFFERENCES:
- Optional[T] = None: Field can be completely missing from JSON
- T = default: Field has default value if missing
- Field(default_factory=list): Creates new list instance per model
"""

# ============================================================================
# SECTION 8: SUMMARY & WHAT YOU LEARNED
# ============================================================================

"""
🎉 MASTER OF DATA MODELS! You now understand Pydantic validation!

WHAT YOU LEARNED:
=================

1. ✅ Pydantic BaseModel
   - Defines data structure and validation rules
   - Automatic type conversion and validation
   - Clear error messages for invalid data

2. ✅ Field Constraints
   - min_length, max_length for strings
   - gt, ge, lt, le for numbers
   - regex patterns and descriptions
   - Automatic API documentation generation

3. ✅ Custom Validators
   - @validator decorators for business logic
   - Cross-field validation
   - Data normalization (lowercase, strip)
   - Custom error messages

4. ✅ Nested Models
   - Complex data structures with Address, OrderItem, Order
   - Recursive validation of nested objects
   - Lists of objects (List[OrderItem])
   - Optional nested objects

5. ✅ Response Models
   - Filter sensitive data from responses
   - Ensure API contract consistency
   - Generate accurate documentation
   - Type safety for API consumers

6. ✅ Error Handling
   - Custom exception handlers
   - Structured error responses
   - Validation error formatting
   - HTTP status codes

7. ✅ Optional Fields & Defaults
   - Optional[T] vs default values
   - Field(default_factory=...) for mutable defaults
   - Flexible API design

VALIDATION WORKFLOW:
===================
1. Client sends JSON → FastAPI receives
2. FastAPI parses JSON → Python dict
3. Pydantic validates → Converts to model object
4. Your function runs → Returns response
5. Pydantic serializes → JSON response sent

NEXT TUTORIAL:
==============
tutorial_3_crud_operations.py - Learn database operations,
HTTP status codes, and full CRUD implementation!
"""

# ============================================================================
# HOW TO RUN THIS TUTORIAL
# ============================================================================

if __name__ == "__main__":
    print("🚀 FastAPI Tutorial 2: Data Models & Validation")
    print("=" * 60)
    print("\n📚 What you'll learn:")
    print("✅ Pydantic BaseModel and automatic validation")
    print("✅ Field constraints (min_length, gt, regex, etc.)")
    print("✅ Custom validators with @validator")
    print("✅ Nested models and complex data structures")
    print("✅ Response models for API contracts")
    print("✅ Error handling and validation messages")
    print("✅ Optional fields and default values")
    print("\n🚀 To run:")
    print("python -m uvicorn tutorial_2_data_models:app --reload")
    print("\n📖 Visit:")
    print("http://localhost:8000/docs (Try the validation examples!)")
    print("\n💡 Tip: Send invalid data to see validation errors!")

