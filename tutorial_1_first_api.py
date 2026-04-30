"""
FASTAPI TUTORIAL 1: YOUR FIRST API - DETAILED EXPLANATION
========================================================

🎯 OBJECTIVE: Build your first FastAPI application and understand every line of code.

📚 WHAT YOU'LL LEARN:
- How to create a FastAPI application instance
- How HTTP GET requests work in FastAPI
- How path parameters work internally
- How query parameters work internally
- How FastAPI handles different data types
- How the automatic documentation works

🚀 RUN THIS TUTORIAL:
    python -m uvicorn tutorial_1_first_api:app --reload

Then visit:
    http://localhost:8000/docs (Interactive API docs)
    http://localhost:8000/redoc (Alternative docs)
"""

from fastapi import FastAPI

# ============================================================================
# STEP 1: CREATING YOUR FASTAPI APPLICATION
# ============================================================================

# This creates your main FastAPI application instance
# Think of this as your web server - it handles all incoming HTTP requests
app = FastAPI(
    title="My First FastAPI App",      # Shows in API documentation
    description="Learning FastAPI basics",  # Description in docs
    version="1.0.0"                    # API version
)

"""
WHAT HAPPENS WHEN YOU CREATE FastAPI()?

Internally, FastAPI:
1. Creates an ASGI application instance (based on Starlette)
2. Sets up routing system to handle different URLs
3. Prepares automatic API documentation generation
4. Initializes dependency injection system
5. Sets up error handling and validation systems

The 'app' object is now ready to receive HTTP requests and route them
to the appropriate handler functions.
"""

# ============================================================================
# STEP 2: YOUR FIRST ENDPOINT - HELLO WORLD
# ============================================================================

@app.get("/")
def read_root():
    """
    This is your first API endpoint!

    WHAT THIS DOES:
    - @app.get("/") is a DECORATOR that tells FastAPI:
      "When someone makes a GET request to the root URL (/), call this function"

    - The function name 'read_root' doesn't matter for the API
      (it's just for your code organization)

    - When called, it returns a Python dictionary
    - FastAPI automatically converts this to JSON for the HTTP response

    TRY IT:
    Visit http://localhost:8000/ in your browser
    You'll see: {"message": "Hello, World!"}
    """
    return {"message": "Hello, World!"}

"""
HOW THIS WORKS INTERNALLY:

1. User types http://localhost:8000/ in browser
2. Browser sends HTTP GET request to your server
3. Uvicorn (ASGI server) receives the request
4. Uvicorn passes request to your FastAPI app
5. FastAPI checks routing table: "GET /" → call read_root()
6. Your function runs and returns {"message": "Hello, World!"}
7. FastAPI converts dict to JSON string
8. FastAPI creates HTTP response with JSON body
9. Response sent back to browser
10. Browser displays the JSON

HTTP REQUEST FLOW:
Browser → Uvicorn → FastAPI → Your Function → FastAPI → Uvicorn → Browser
"""

# ============================================================================
# STEP 3: PATH PARAMETERS - DYNAMIC URLS
# ============================================================================

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """
    Path parameters make URLs dynamic.

    URL STRUCTURE: /users/{user_id}
    - The {user_id} part is a PLACEHOLDER
    - FastAPI extracts the actual value from the URL
    - The : int tells FastAPI to convert the string to integer

    EXAMPLES:
    - URL: /users/123 → user_id = 123 (integer)
    - URL: /users/456 → user_id = 456 (integer)

    WHAT HAPPENS INTERNALLY:
    1. FastAPI parses the URL pattern /users/{user_id}
    2. When request comes: /users/123
    3. FastAPI extracts "123" from URL
    4. Converts "123" to int (123) because of type hint
    5. Calls your function with user_id=123
    """
    return {
        "user_id": user_id,                    # The extracted integer
        "user_name": f"User {user_id}",       # String formatting
        "email": f"user{user_id}@example.com", # Dynamic email
        "type": "path_parameter"               # Just to show this is from path
    }

"""
PATH PARAMETER VALIDATION:

FastAPI automatically validates path parameters based on type hints:

✅ Valid: /users/123 → user_id=123 (int)
❌ Invalid: /users/abc → Returns 422 error (can't convert "abc" to int)

This is why type hints are so important in FastAPI - they provide
automatic validation and conversion!
"""

# ============================================================================
# STEP 4: MULTIPLE PATH PARAMETERS
# ============================================================================

@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    """
    Multiple path parameters in one URL.

    URL PATTERN: /users/{user_id}/posts/{post_id}
    - Extracts both user_id and post_id from URL
    - Both are converted to integers

    EXAMPLE: /users/123/posts/456
    RESULT: user_id=123, post_id=456
    """
    return {
        "user_id": user_id,
        "post_id": post_id,
        "post_title": f"Post {post_id} by User {user_id}",
        "content": f"This is the content of post {post_id}...",
        "url": f"/users/{user_id}/posts/{post_id}"
    }

"""
URL PARSING LOGIC:

For URL: /users/123/posts/456
FastAPI internally:
1. Matches pattern: /users/{user_id}/posts/{post_id}
2. Extracts segments: ["users", "123", "posts", "456"]
3. Maps to parameters: user_id="123", post_id="456"
4. Converts types: user_id=123, post_id=456
5. Calls function with converted values
"""

# ============================================================================
# STEP 5: QUERY PARAMETERS - OPTIONAL FILTERS
# ============================================================================

@app.get("/search")
def search_items(q: str = None, limit: int = 10, category: str = "all"):
    """
    Query parameters appear after ? in URLs.

    URL FORMAT: /search?q=laptop&limit=5&category=electronics

    WHAT MAKES QUERY PARAMETERS DIFFERENT:
    - They have DEFAULT VALUES (q=None, limit=10, category="all")
    - They are OPTIONAL - can be omitted
    - They appear after ? separated by &

    EXAMPLES:
    /search → q=None, limit=10, category="all"
    /search?q=laptop → q="laptop", limit=10, category="all"
    /search?q=phone&limit=20 → q="phone", limit=20, category="all"
    /search?category=books&limit=5 → q=None, limit=5, category="books"
    """
    # Simulate search logic
    if q is None:
        return {
            "message": "Please provide a search query",
            "example": "/search?q=laptop",
            "parameters_used": {
                "q": q,
                "limit": limit,
                "category": category
            }
        }

    # Simulate search results
    results = []
    for i in range(1, min(limit + 1, 11)):  # Max 10 results for demo
        results.append({
            "id": i,
            "name": f"{q} {i}",
            "category": category,
            "price": i * 10.99
        })

    return {
        "query": q,
        "category": category,
        "limit": limit,
        "total_results": len(results),
        "results": results,
        "search_url": f"/search?q={q}&limit={limit}&category={category}"
    }

"""
QUERY PARAMETER INTERNALS:

For URL: /search?q=laptop&limit=5&category=electronics

FastAPI internally:
1. Parses query string: "q=laptop&limit=5&category=electronics"
2. Splits by &: ["q=laptop", "limit=5", "category=electronics"]
3. Splits by =: {"q": "laptop", "limit": "5", "category": "electronics"}
4. Converts types: q="laptop", limit=5, category="electronics"
5. Uses defaults for missing params
6. Calls function with final values

KEY DIFFERENCE FROM PATH PARAMS:
- Path params are REQUIRED and part of URL structure
- Query params are OPTIONAL and can have defaults
"""

# ============================================================================
# STEP 6: MIXED PARAMETERS (PATH + QUERY)
# ============================================================================

@app.get("/users/{user_id}/posts")
def get_user_posts(
    user_id: int,           # Path parameter (required)
    limit: int = 10,        # Query parameter (optional, default 10)
    published: bool = True  # Query parameter (optional, default True)
):
    """
    Combining path parameters with query parameters.

    URL PATTERN: /users/{user_id}/posts
    - user_id: Extracted from URL path (required)
    - limit: Query parameter (optional, defaults to 10)
    - published: Query parameter (optional, defaults to True)

    EXAMPLES:
    /users/123/posts → user_id=123, limit=10, published=True
    /users/123/posts?limit=5 → user_id=123, limit=5, published=True
    /users/123/posts?published=false&limit=20 → user_id=123, limit=20, published=False
    """
    # Simulate getting posts for user
    posts = []
    for i in range(1, limit + 1):
        posts.append({
            "id": i,
            "user_id": user_id,
            "title": f"Post {i} by User {user_id}",
            "published": published,
            "content": f"Content of post {i}..."
        })

    return {
        "user_id": user_id,
        "total_posts": len(posts),
        "published_only": published,
        "limit": limit,
        "posts": posts
    }

"""
PARAMETER PRECEDENCE:

When FastAPI processes a request like:
GET /users/123/posts?limit=5&published=false

It follows this order:
1. Match URL pattern: /users/{user_id}/posts
2. Extract path params: user_id = "123" → 123 (int)
3. Parse query string: limit="5" → 5 (int), published="false" → False (bool)
4. Apply defaults for missing params
5. Call function with all parameters
"""

# ============================================================================
# STEP 7: DIFFERENT HTTP METHODS
# ============================================================================

@app.post("/users")
def create_user(name: str, email: str, age: int = 18):
    """
    POST method for creating new resources.

    POST is used when you want to CREATE something new.
    Unlike GET, POST can have a request body.

    In this example, we're using query parameters for simplicity,
    but in real apps you'd use request body (covered in next tutorial).

    EXAMPLE REQUEST:
    POST /users?name=John&email=john@example.com&age=25

    WHAT MAKES POST DIFFERENT:
    - Used for creating resources
    - Can modify server state
    - Usually has request body
    - Returns 201 Created status (by default in FastAPI)
    """
    # Simulate creating user (in real app, save to database)
    user_id = hash(f"{name}{email}") % 10000  # Simple ID generation

    return {
        "action": "created",
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
            "age": age,
            "created": True
        },
        "http_method": "POST"
    }

@app.put("/users/{user_id}")
def update_user(user_id: int, name: str = None, email: str = None):
    """
    PUT method for updating existing resources.

    PUT is used to UPDATE/CREATE a resource at a specific URL.
    It's idempotent - calling it multiple times has same effect.

    EXAMPLE REQUEST:
    PUT /users/123?name=Jane&email=jane@example.com

    WHAT MAKES PUT DIFFERENT:
    - Updates existing resource
    - Can create if resource doesn't exist
    - Idempotent (safe to call multiple times)
    - Usually replaces entire resource
    """
    return {
        "action": "updated",
        "user_id": user_id,
        "updates": {
            "name": name,
            "email": email
        },
        "http_method": "PUT",
        "idempotent": True
    }

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """
    DELETE method for removing resources.

    DELETE is used to remove a resource from the server.

    EXAMPLE REQUEST:
    DELETE /users/123

    WHAT MAKES DELETE DIFFERENT:
    - Removes resource
    - Usually returns 204 No Content (no response body)
    - Idempotent (deleting already deleted item is OK)
    """
    return {
        "action": "deleted",
        "user_id": user_id,
        "http_method": "DELETE",
        "status": "success"
    }

"""
HTTP METHODS SUMMARY:

METHOD    | PURPOSE              | IDEMPOTENT | SAFE | REQUEST BODY
----------|----------------------|-------------|------|-------------
GET       | Retrieve data        | Yes         | Yes  | No
POST      | Create resource      | No          | No   | Yes
PUT       | Update/Create        | Yes         | No   | Yes
DELETE    | Remove resource      | Yes         | No   | No
PATCH     | Partial update       | No          | No   | Yes

IDEMPOTENT: Multiple calls = same result
SAFE: Doesn't modify server state
"""

# ============================================================================
# STEP 8: AUTOMATIC API DOCUMENTATION
# ============================================================================

@app.get("/info")
def get_api_info():
    """
    This endpoint demonstrates automatic documentation.

    The docstring you write here appears in the API documentation!

    Visit /docs to see how FastAPI automatically creates:
    - Interactive API testing interface
    - Parameter descriptions
    - Response examples
    - Error responses
    """
    return {
        "api_name": "FastAPI Tutorial 1",
        "version": "1.0.0",
        "endpoints": [
            "GET /",
            "GET /users/{user_id}",
            "GET /users/{user_id}/posts/{post_id}",
            "GET /search",
            "GET /users/{user_id}/posts",
            "POST /users",
            "PUT /users/{user_id}",
            "DELETE /users/{user_id}",
            "GET /info"
        ],
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        }
    }

"""
HOW AUTOMATIC DOCUMENTATION WORKS:

1. FastAPI analyzes your function signatures and type hints
2. Reads your docstrings
3. Extracts parameter information and validation rules
4. Generates OpenAPI 3.0 specification (JSON format)
5. Serves interactive documentation at /docs and /redoc

WHY THIS IS POWERFUL:
- Documentation is ALWAYS up-to-date with your code
- Interactive testing interface (try endpoints directly)
- Client SDK generation for frontend teams
- API contract for testing teams
"""

# ============================================================================
# STEP 9: SUMMARY & WHAT YOU LEARNED
# ============================================================================

"""
🎉 CONGRATULATIONS! You built your first FastAPI application!

WHAT YOU LEARNED:
=================

1. ✅ FastAPI Application Instance
   - app = FastAPI() creates your web application
   - Handles routing, validation, documentation automatically

2. ✅ HTTP GET Requests
   - @app.get("/path") decorator defines endpoints
   - Functions return Python dicts, FastAPI converts to JSON

3. ✅ Path Parameters
   - /users/{user_id} extracts values from URL
   - Type hints (: int) automatically convert and validate
   - Required parameters (no defaults)

4. ✅ Query Parameters
   - Appear after ? in URL: /search?q=value&limit=10
   - Optional with default values
   - Can be omitted from URL

5. ✅ Multiple HTTP Methods
   - GET: Retrieve data (safe, idempotent)
   - POST: Create resources (not idempotent)
   - PUT: Update resources (idempotent)
   - DELETE: Remove resources (idempotent)

6. ✅ Automatic Documentation
   - /docs: Interactive Swagger UI
   - /redoc: Alternative documentation
   - Generated from your code automatically

7. ✅ Request Flow Understanding
   - Browser → Uvicorn → FastAPI → Your Function → Response

KEY CONCEPTS MASTERED:
====================
- URL routing and parameter extraction
- HTTP methods and their purposes
- Type conversion and validation
- RESTful API design principles
- Automatic API documentation

NEXT TUTORIAL:
==============
tutorial_2_data_models.py - Learn about Pydantic models,
request bodies, and advanced validation!
"""

# ============================================================================
# HOW TO RUN THIS TUTORIAL
# ============================================================================

if __name__ == "__main__":
    print("🚀 FastAPI Tutorial 1: Your First API")
    print("=" * 50)
    print("\n📚 What you'll learn:")
    print("✅ Creating FastAPI applications")
    print("✅ HTTP GET, POST, PUT, DELETE methods")
    print("✅ Path parameters and query parameters")
    print("✅ URL routing and parameter extraction")
    print("✅ Automatic API documentation")
    print("✅ Understanding HTTP request/response flow")
    print("\n🚀 To run:")
    print("python -m uvicorn tutorial_1_first_api:app --reload")
    print("\n📖 Then visit:")
    print("http://localhost:8000/docs (Interactive docs)")
    print("http://localhost:8000/redoc (Alternative docs)")
    print("http://localhost:8000/ (Your first endpoint)")

