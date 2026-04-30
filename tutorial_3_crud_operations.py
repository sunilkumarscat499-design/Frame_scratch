"""
FASTAPI TUTORIAL 3: CRUD OPERATIONS & DATABASE - DETAILED EXPLANATION
====================================================================

🎯 OBJECTIVE: Master full CRUD operations and understand database integration.

📚 WHAT YOU'LL LEARN:
- Complete CRUD implementation (Create, Read, Update, Delete)
- HTTP status codes and their meanings
- In-memory database operations
- Error handling patterns
- Data persistence concepts
- RESTful API design principles

🚀 RUN THIS TUTORIAL:
    python -m uvicorn tutorial_3_crud_operations:app --reload

Visit: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os

app = FastAPI(
    title="FastAPI CRUD Operations Tutorial",
    description="Mastering database operations and RESTful APIs",
    version="3.0.0"
)

# ============================================================================
# SECTION 1: DATA MODELS FOR CRUD
# ============================================================================

class Item(BaseModel):
    """
    Item model for CRUD operations.

    This represents a product or item in our system.
    We'll perform full CRUD operations on this model.
    """
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: str = Field(..., min_length=5, max_length=500, description="Item description")
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    quantity: int = Field(default=1, ge=0, description="Stock quantity")
    category: str = Field(..., min_length=2, max_length=50, description="Item category")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ItemUpdate(BaseModel):
    """
    Model for partial updates (PATCH operations).

    Only includes fields that can be updated.
    All fields are optional since we might update only some of them.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    category: Optional[str] = None

# ============================================================================
# SECTION 2: IN-MEMORY DATABASE SIMULATION
# ============================================================================

# Simple in-memory database (list of dictionaries)
# In production, this would be a real database like PostgreSQL, MySQL, etc.
items_db: List[Dict[str, Any]] = []

# Auto-incrementing ID counter
next_item_id = 1

def get_next_id() -> int:
    """Generate next available ID"""
    global next_item_id
    item_id = next_item_id
    next_item_id += 1
    return item_id

def find_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Find item by ID in database"""
    for item in items_db:
        if item["id"] == item_id:
            return item
    return None

def save_item_to_db(item_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Save item to database (add timestamps)"""
    now = datetime.now()

    if "id" not in item_dict:
        item_dict["id"] = get_next_id()
        item_dict["created_at"] = now
    else:
        # Update existing item
        existing = find_item_by_id(item_dict["id"])
        if existing:
            item_dict["created_at"] = existing["created_at"]

    item_dict["updated_at"] = now
    return item_dict

"""
DATABASE CONCEPTS EXPLAINED:

IN-MEMORY DATABASE:
- Data stored in Python list (items_db)
- Lost when server restarts
- Good for learning, bad for production

PRODUCTION DATABASES:
- PostgreSQL: Most popular, feature-rich
- MySQL: Widely used, good performance
- SQLite: File-based, good for small apps
- MongoDB: NoSQL, document-based

DATABASE OPERATIONS:
- Create: INSERT new record
- Read: SELECT existing records
- Update: UPDATE existing record
- Delete: DELETE existing record

This tutorial simulates database operations with Python lists.
"""

# ============================================================================
# SECTION 3: CREATE (POST) - ADDING NEW DATA
# ============================================================================

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    """
    CREATE: Add a new item to the database.

    WHAT HAPPENS INTERNALLY:
    1. FastAPI validates the input data against Item model
    2. Converts Pydantic model to dictionary
    3. Adds ID and timestamps
    4. Saves to database (items_db list)
    5. Returns the created item

    HTTP STATUS: 201 Created (standard for successful creation)

    EXAMPLE REQUEST BODY:
    {
        "name": "Wireless Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "price": 199.99,
        "quantity": 25,
        "category": "electronics"
    }

    RESPONSE INCLUDES:
    - All original fields
    - Auto-generated ID
    - created_at and updated_at timestamps
    """
    # Convert Pydantic model to dictionary
    item_dict = item.dict()

    # Save to database (adds ID and timestamps)
    saved_item = save_item_to_db(item_dict)

    # Add to our in-memory database
    items_db.append(saved_item)

    print(f"✅ CREATED: Item '{saved_item['name']}' with ID {saved_item['id']}")

    return saved_item

"""
CREATE OPERATION DETAILS:

HTTP METHOD: POST
URL: /items
STATUS CODE: 201 Created
REQUEST BODY: Item data (JSON)
RESPONSE: Created Item object

WHY POST?
- POST is for creating new resources
- It's not idempotent (calling multiple times creates multiple items)
- Returns 201 Created status code
- Usually includes the created resource in response

DATABASE EQUIVALENT:
INSERT INTO items (name, description, price, quantity, category)
VALUES ('Headphones', 'Wireless headphones', 199.99, 25, 'electronics');
"""

# ============================================================================
# SECTION 4: READ (GET) - RETRIEVING DATA
# ============================================================================

@app.get("/items", response_model=List[Item])
def get_all_items(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    READ: Get all items with filtering and pagination.

    QUERY PARAMETERS:
    - skip: Number of items to skip (for pagination)
    - limit: Maximum number of items to return
    - category: Filter by category
    - min_price, max_price: Price range filtering

    EXAMPLES:
    GET /items → First 10 items
    GET /items?skip=10&limit=5 → Items 11-15
    GET /items?category=electronics → Electronics only
    GET /items?min_price=50&max_price=200 → Price range

    WHAT HAPPENS INTERNALLY:
    1. Start with all items in database
    2. Apply filters (category, price range)
    3. Apply pagination (skip, limit)
    4. Return filtered results
    """
    # Start with all items
    filtered_items = items_db.copy()

    # Apply category filter
    if category:
        filtered_items = [item for item in filtered_items if item["category"] == category]

    # Apply price filters
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] >= min_price]

    if max_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] <= max_price]

    # Apply pagination
    total_items = len(filtered_items)
    paginated_items = filtered_items[skip : skip + limit]

    print(f"📖 READ: Returned {len(paginated_items)} items (filtered from {total_items})")

    return paginated_items

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    """
    READ: Get a specific item by ID.

    PATH PARAMETER: item_id (extracted from URL)

    WHAT HAPPENS:
    1. Extract item_id from URL (/items/123 → item_id=123)
    2. Search database for item with this ID
    3. If found: return item
    4. If not found: return 404 Not Found error

    HTTP STATUS CODES:
    - 200 OK: Item found and returned
    - 404 Not Found: Item doesn't exist
    """
    item = find_item_by_id(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )

    print(f"📖 READ: Retrieved item '{item['name']}' (ID: {item_id})")

    return item

@app.get("/items/search", response_model=List[Item])
def search_items(q: str, limit: int = 10):
    """
    READ: Search items by name or description.

    QUERY PARAMETERS:
    - q: Search query (required)
    - limit: Maximum results

    SEARCH LOGIC:
    - Case-insensitive search
    - Searches both name and description fields
    - Returns up to 'limit' results

    EXAMPLE: GET /items/search?q=laptop&limit=5
    """
    if not q or len(q.strip()) == 0:
        return []

    query = q.lower().strip()
    results = []

    for item in items_db:
        # Search in name and description
        if (query in item["name"].lower() or
            query in item.get("description", "").lower()):
            results.append(item)

            if len(results) >= limit:
                break

    print(f"🔍 SEARCH: Found {len(results)} items for query '{q}'")

    return results

"""
READ OPERATION DETAILS:

HTTP METHOD: GET
STATUS CODE: 200 OK
REQUEST BODY: None (GET requests don't have bodies)
RESPONSE: Requested data

WHY GET?
- GET is for retrieving data
- It's safe (doesn't modify data)
- It's idempotent (multiple calls = same result)
- Can be cached by browsers/proxies
- Can be bookmarked

DATABASE EQUIVALENT:
SELECT * FROM items WHERE category = 'electronics' LIMIT 10 OFFSET 0;
"""

# ============================================================================
# SECTION 5: UPDATE (PUT/PATCH) - MODIFYING DATA
# ============================================================================

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    """
    UPDATE (Full): Replace entire item.

    PUT replaces the entire resource with new data.
    All fields must be provided (even if unchanged).

    WHAT HAPPENS:
    1. Find existing item by ID
    2. If not found: 404 error
    3. Replace entire item with new data
    4. Update timestamp
    5. Return updated item

    EXAMPLE REQUEST:
    PUT /items/123
    {
        "name": "Updated Laptop",
        "description": "Updated description",
        "price": 899.99,
        "quantity": 15,
        "category": "electronics"
    }

    NOTE: All fields required, even if unchanged!
    """
    # Find existing item
    existing_item = find_item_by_id(item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )

    # Replace entire item
    updated_item_dict = item.dict()
    updated_item_dict["id"] = item_id  # Keep original ID
    updated_item_dict["created_at"] = existing_item["created_at"]  # Keep creation time
    updated_item_dict["updated_at"] = datetime.now()  # Update modification time

    # Replace in database
    index = items_db.index(existing_item)
    items_db[index] = updated_item_dict

    print(f"🔄 UPDATED (PUT): Item '{updated_item_dict['name']}' (ID: {item_id})")

    return updated_item_dict

@app.patch("/items/{item_id}", response_model=Item)
def partial_update_item(item_id: int, item_update: ItemUpdate):
    """
    UPDATE (Partial): Update only specified fields.

    PATCH updates only the fields you provide.
    Other fields remain unchanged.

    WHAT HAPPENS:
    1. Find existing item
    2. Create copy of existing data
    3. Update only provided fields
    4. Save back to database

    EXAMPLE REQUEST:
    PATCH /items/123
    {
        "price": 799.99,
        "quantity": 20
    }

    Only price and quantity change, other fields stay the same!
    """
    # Find existing item
    existing_item = find_item_by_id(item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )

    # Start with existing data
    updated_item = existing_item.copy()

    # Update only provided fields (exclude None values)
    update_data = item_update.dict(exclude_unset=True)
    updated_item.update(update_data)

    # Update timestamp
    updated_item["updated_at"] = datetime.now()

    # Save to database
    index = items_db.index(existing_item)
    items_db[index] = updated_item

    print(f"🔄 UPDATED (PATCH): Item '{updated_item['name']}' (ID: {item_id}) - {list(update_data.keys())} changed")

    return updated_item

"""
UPDATE OPERATIONS COMPARISON:

PUT (Full Update):
- Replaces entire resource
- All fields must be provided
- Missing fields are set to defaults
- Idempotent (same result if called multiple times)

PATCH (Partial Update):
- Updates only specified fields
- Other fields remain unchanged
- More flexible for partial changes
- Also idempotent

DATABASE EQUIVALENT:
PUT:  UPDATE items SET name=?, description=?, price=?, ... WHERE id=?
PATCH: UPDATE items SET price=? WHERE id=? (only changed fields)
"""

# ============================================================================
# SECTION 6: DELETE (DELETE) - REMOVING DATA
# ============================================================================

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    """
    DELETE: Remove an item from the database.

    HTTP STATUS: 204 No Content
    - 204 means "success, but no response body"
    - Standard for DELETE operations

    WHAT HAPPENS:
    1. Find item by ID
    2. If not found: 404 error
    3. Remove from database
    4. Return 204 (no content)

    WHY 204 NO CONTENT?
    - DELETE operations don't need to return data
    - Client knows deletion was successful from status code
    - Saves bandwidth
    """
    # Find item
    item = find_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )

    # Remove from database
    items_db.remove(item)

    print(f"🗑️ DELETED: Item '{item['name']}' (ID: {item_id})")

    # 204 No Content - no return statement needed

"""
DELETE OPERATION DETAILS:

HTTP METHOD: DELETE
STATUS CODE: 204 No Content
REQUEST BODY: None
RESPONSE BODY: None (just status code)

WHY DELETE?
- DELETE is for removing resources
- It's idempotent (deleting already deleted item is OK)
- Usually returns 204 No Content

DATABASE EQUIVALENT:
DELETE FROM items WHERE id = ?;
"""

# ============================================================================
# SECTION 7: BULK OPERATIONS
# ============================================================================

@app.post("/items/bulk", response_model=List[Item])
def create_items_bulk(items: List[Item]):
    """
    CREATE BULK: Add multiple items at once.

    REQUEST BODY: Array of Item objects
    RESPONSE: Array of created Item objects

    EXAMPLE REQUEST:
    [
        {
            "name": "Item 1",
            "description": "Description 1",
            "price": 10.99,
            "category": "test"
        },
        {
            "name": "Item 2",
            "description": "Description 2",
            "price": 20.99,
            "category": "test"
        }
    ]
    """
    created_items = []

    for item in items:
        item_dict = item.dict()
        saved_item = save_item_to_db(item_dict)
        items_db.append(saved_item)
        created_items.append(saved_item)

    print(f"✅ BULK CREATED: {len(created_items)} items")

    return created_items

@app.delete("/items/bulk", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_items():
    """
    DELETE ALL: Remove all items (dangerous operation!).

    This is for testing/demo purposes only.
    In production, you'd add authentication and confirmation.

    WARNING: This deletes ALL data!
    """
    global items_db, next_item_id
    deleted_count = len(items_db)

    items_db.clear()
    next_item_id = 1  # Reset ID counter

    print(f"🗑️ BULK DELETED: {deleted_count} items")

    # 204 No Content

# ============================================================================
# SECTION 8: STATISTICS & METADATA
# ============================================================================

@app.get("/items/stats")
def get_items_stats():
    """
    Get statistics about the items database.

    Useful for dashboards and monitoring.
    Returns metadata about the data.
    """
    if not items_db:
        return {
            "total_items": 0,
            "total_value": 0.0,
            "average_price": 0.0,
            "categories": [],
            "price_range": {"min": 0, "max": 0},
            "last_updated": None
        }

    # Calculate statistics
    total_items = len(items_db)
    total_value = sum(item["price"] * item["quantity"] for item in items_db)
    average_price = sum(item["price"] for item in items_db) / total_items

    categories = list(set(item["category"] for item in items_db))
    prices = [item["price"] for item in items_db]
    min_price, max_price = min(prices), max(prices)

    last_updated = max(item["updated_at"] for item in items_db)

    return {
        "total_items": total_items,
        "total_value": round(total_value, 2),
        "average_price": round(average_price, 2),
        "categories": sorted(categories),
        "price_range": {
            "min": min_price,
            "max": max_price
        },
        "last_updated": last_updated.isoformat() if last_updated else None
    }

@app.get("/items/categories")
def get_categories():
    """
    Get all unique categories with counts.
    """
    category_counts = {}
    for item in items_db:
        category = item["category"]
        category_counts[category] = category_counts.get(category, 0) + 1

    return {
        "categories": [
            {"name": cat, "count": count}
            for cat, count in sorted(category_counts.items())
        ],
        "total_categories": len(category_counts)
    }

# ============================================================================
# SECTION 9: ERROR HANDLING PATTERNS
# ============================================================================

@app.get("/items/{item_id}/error-demo")
def error_demo(item_id: int):
    """
    Demonstrate different error scenarios.

    Try different item_ids:
    - 999: Not found (404)
    - -1: Validation error (422 from path parameter)
    - 0: Custom validation error
    """
    if item_id == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID cannot be zero"
        )

    if item_id == 999:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom error message for item 999"
        )

    return {"item_id": item_id, "message": "No error occurred"}

# ============================================================================
# SECTION 10: SUMMARY & CRUD PRINCIPLES
# ============================================================================

"""
🎉 CRUD MASTER! You now understand complete database operations!

WHAT YOU LEARNED:
=================

1. ✅ CREATE (POST)
   - Adding new data to database
   - Auto-generating IDs and timestamps
   - HTTP 201 Created status
   - Input validation

2. ✅ READ (GET)
   - Retrieving data with filtering
   - Pagination (skip/limit)
   - Search functionality
   - HTTP 200 OK status

3. ✅ UPDATE (PUT/PATCH)
   - PUT: Full resource replacement
   - PATCH: Partial field updates
   - Timestamp management
   - Data validation

4. ✅ DELETE (DELETE)
   - Removing data from database
   - HTTP 204 No Content status
   - Idempotent operations

5. ✅ HTTP STATUS CODES
   - 200: Success
   - 201: Created
   - 204: No Content
   - 400: Bad Request
   - 404: Not Found
   - 422: Validation Error

6. ✅ ERROR HANDLING
   - HTTPException for API errors
   - Appropriate status codes
   - Descriptive error messages

7. ✅ BULK OPERATIONS
   - Creating multiple items
   - Deleting all items
   - Batch processing

CRUD PRINCIPLES:
===============
- CREATE: POST /resource
- READ: GET /resource, GET /resource/{id}
- UPDATE: PUT /resource/{id}, PATCH /resource/{id}
- DELETE: DELETE /resource/{id}

DATABASE ABSTRACTION:
====================
This tutorial uses in-memory lists, but the same patterns apply to:
- PostgreSQL with SQLAlchemy
- MySQL with Peewee
- MongoDB with Motor (async)
- SQLite for small applications

NEXT TUTORIAL:
==============
tutorial_4_advanced_features.py - Authentication, file uploads,
background tasks, and production-ready features!
"""

# ============================================================================
# HOW TO RUN THIS TUTORIAL
# ============================================================================

if __name__ == "__main__":
    print("🚀 FastAPI Tutorial 3: CRUD Operations & Database")
    print("=" * 60)
    print("\n📚 What you'll learn:")
    print("✅ Complete CRUD operations (Create, Read, Update, Delete)")
    print("✅ HTTP status codes and RESTful design")
    print("✅ In-memory database operations")
    print("✅ Error handling patterns")
    print("✅ Filtering, pagination, and search")
    print("✅ Bulk operations")
    print("✅ Data validation and timestamps")
    print("\n🚀 To run:")
    print("python -m uvicorn tutorial_3_crud_operations:app --reload")
    print("\n📖 Visit:")
    print("http://localhost:8000/docs (Try all CRUD operations!)")
    print("\n💡 Tip: Create some items first, then try updating/deleting them!")

