# API Endpoint Implementation Plan: Categories Endpoint

## 1. Overview of the Endpoint
`/categories` endpoint group provides comprehensive lifecycle management for user-defined expense categories, enriched with AI-driven suggestions. It includes:
- **Listing categories**: Retrieve all categories belonging to the authenticated user, including the automatically created default "Uncategorized."
- **Reading a single category**: Fetch metadata of a specific category by its UUID, enforcing access control via RLS.
- **Creating categories**: Allow users to define custom categories with unique names (≤30 chars). The system enforces one default category per user.
- **Updating categories**: Rename existing categories, maintaining uniqueness constraints and prohibiting changes to the default category flag.
- **Deleting categories**: Remove non-default categories; deletion attempts on the default category will fail with a 400 Bad Request.
- **AI Suggestions**: Analyze expense `description` and `amount` to propose up to 3 relevant category suggestions, ranked by historical usage.

Key business rules:
- Each user receives exactly one default category ("Uncategorized") upon registration via a database trigger.
- Category names must be unique per user and limited to 30 characters.
- The default category cannot be deleted or renamed through the API.

Security & Data Integrity:
- Supabase Row Level Security (RLS) ensures users can only access their own categories.
- JWT Bearer tokens authenticate all requests; expired or missing tokens return 401 Unauthorized.

Technical Context:
- Implemented as a Flask Blueprint with Pydantic schemas for request validation and response serialization.
- Service layer isolates business logic and communicates with the Supabase client or ORM.
- Controller layer handles routing, error mapping, and invokes service methods.

Endpoints covered in this plan:
- GET `/categories`
- POST `/categories`
- GET `/categories/{id}`
- PUT `/categories/{id}`
- DELETE `/categories/{id}`
- GET `/categories/suggestions`

## 2. Request Details

### GET /categories
- HTTP Method: GET
- URL: `/categories`
- Headers:
  - `Authorization: Bearer <access_token>` (required)
- Parameters:
  - None

### POST /categories
- HTTP Method: POST
- URL: `/categories`
- Headers:
  - `Authorization: Bearer <access_token>`
- Body (JSON):
  ```json
  { "name": "Transport" }
  ```
- Validation:
  - `name` required, type `string`, maximum 30 characters

### GET /categories/:id
- HTTP Method: GET
- URL: `/categories/{id}`
- Path:
  - `id` (UUID) – required
- Headers:
  - `Authorization`
- Parameters:
  - None

### PUT /categories/:id
- HTTP Method: PUT
- URL: `/categories/{id}`
- Headers:
  - `Authorization`
- Body (JSON):
  ```json
  { "name": "Groceries" }
  ```
- Validation:
  - `name` required, type `string`, maximum 30 characters

### DELETE /categories/:id
- HTTP Method: DELETE
- URL: `/categories/{id}`
- Headers:
  - `Authorization`
- Parameters:
  - `id` (UUID)

### GET /categories/suggestions
- HTTP Method: GET
- URL: `/categories/suggestions`
- Headers:
  - `Authorization`
- Query Params:
  - `description` (string, required)
  - `amount` (number, required)

## 3. Types Used
- CategoryRead (id: UUID, name: string, is_default: bool)
- CategoryCreate / CategoryUpdate (name: constr(max_length=30))
- CategorySuggestion (id: UUID, name: string, usage_count: int)

## 4. Data Flow
1. **Authorization**: Middleware checks `Authorization`, retrieves `user_id` from token.
2. **Routing (Flask Blueprint)**:  Each path calls the appropriate controller function.
3. **Controller**: Parses request, validates with Pydantic, passes task to `CategoryService`.
4. **Service Layer**: `CategoryService` communicates with Supabase (or ORM):
   - `list_categories(user_id)` → SELECT *
   - `create_category(user_id, name)` → INSERT; throws ConflictError in case of uniqueness violation
   - `get_category(...)`, `update_category(...)`, `delete_category(...)`
   - `suggest_categories(...)` → calls AI module, handles timeout and AI errors
5. **Repository / DB Client**: RLS Supabase ensures that operation affects only own records.
6. **Response**: Service returns DTO, controller serializes to JSON and sends.

## 5. Security Considerations
- **Authorization**: All endpoints protected by JWT token. 401 on missing/invalid.
- **RLS**: Supabase Row Level Security enforces user_id = auth.uid().
- **Validation**: Pydantic protects against SQL injection and invalid types.
- **Permissions**: Check if category belongs to user (for PUT/DELETE/GET/:id).
- **AI Handling**: Timeout and fallback to prevent server blocking.

## 6. Error Handling
| Code  | Condition                                    | Logic                     |
|------|---------------------------------------------|----------------------------|
| 200  | Success GET/PUT                              | —                          |
| 201  | Success POST                                 | —                          |
| 204  | Success DELETE                               | —                          |
| 400  | Validation error (name>30, missing body, DELETE default)| Return JSON with error description; do not log as critical |
| 401  | Missing/invalid token                    | Return 401 Unauthorized     |
| 404  | No category with given id                 | Return 404 Not Found        |
| 409  | Duplicate category name                    | Return 409 Conflict         |
| 502  | AI error/timeout                              | Return 502 Bad Gateway; log error in `logs` |
| 500  | Unexpected error                        | Return 500; log error in `logs` |

For critical errors (AI, DB, unknown) in `except`:
```python
logs.insert({
  'user_id': user_id,
  'category_id': maybe_id,
  'type': 'error',
  'error_code': 'AI_TIMEOUT' or 'DB_ERROR',
  'message': str(exc)
})
```

## 7. Performance Considerations
- **Indexing**: `idx_categories_user_default` when filtering by user_id and is_default.
- **Caching**: Potential cache for category list (short-term).
- **Rate limiting**: Limits for AI-suggestions to avoid overloading.

## 8. Deployment Steps
1. Create Flask Blueprint `categories_bp` and register in the application.
2. Implement Pydantic validators for requests.
3. Create `CategoryService` with listed methods.
4. Add Supabase/ORM client to `CategoryService`.
5. Write controllers for GET/POST/GET/:id/PUT/DELETE, calling Service.
6. Handle exceptions at controller and service levels, mapping to appropriate statuses.
7. Implement AI-suggestions and timeout/fallback.
8. Write unit and integration tests for each endpoint.
9. Update API documentation and add examples (Swagger/OpenAPI).
10. Perform code review, E2E tests, and deploy to staging.
