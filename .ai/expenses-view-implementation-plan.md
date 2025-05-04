# API Endpoint Implementation Plan: Expenses Endpoint

## 1. Endpoint Overview
The `/expenses` endpoint group provides a comprehensive management interface for user expenses, offering the following capabilities:

- **List Expenses**: Retrieve a paginated, filterable, and searchable list of expenses belonging to the authenticated user.
- **Get Expense**: Fetch the details of a single expense by its UUID.
- **Create Expense**: Add a new expense record with required amount, optional description, and optional category assignment (defaults to the user's "Uncategorized" category).
- **Update Expense**: Modify an existing expense's fields (amount, description, category) without triggering AI re-categorization.
- **Delete Expense**: Remove an expense by its identifier.
- **Weekly Summary**: Aggregate and return the total amount spent and transaction count for the current week.

Key business rules and behaviors:
1. **User Isolation**: All operations are scoped to the authenticated user via Supabase Row Level Security (RLS); a user can only view and modify their own records.
2. **Default Category**: If `category_id` is omitted when creating an expense, the service automatically assigns the user's default category ("Uncategorized").
3. **Validation Constraints**:
   - `amount` must be a positive value (greater than 0) with up to two decimal places.
   - `description` is optional and limited to 100 characters.
4. **Pagination & Filtering**:
   - Use `limit` and `offset` for pagination.
   - Support search by `description` (case-insensitive), date range (`date_from`, `date_to`), and amount range (`amount_min`, `amount_max`).
5. **Summary Period**: The `/expenses/summary` endpoint currently supports a single `weekly` period parameter; future expansions may include monthly or custom intervals.
6. **Audit Logging**: Create audit log entries in the `logs` table for create, update, and delete operations (type = `info` on success, `error` on failure).
7. **Error Handling**: Consistent HTTP status codes for validation errors (400), unauthorized access (401), resource not found (404), and server errors (500).

## 2. Request Details

### 2.1 GET /expenses
- HTTP Method: GET
- URL: `/expenses`
- Headers:
  - `Authorization: Bearer <access_token>` (required)
- Query Parameters:
  - `limit` (integer, optional, default = 20, max = 100)
  - `offset` (integer, optional, default = 0)
  - `search` (string, optional)
  - `date_from` (ISO 8601 date, optional)
  - `date_to` (ISO 8601 date, optional)
  - `amount_min` (number, optional)
  - `amount_max` (number, optional)
- Request Body: None

### 2.2 GET /expenses/{id}
- HTTP Method: GET
- URL: `/expenses/{id}`
- Headers:
  - `Authorization: Bearer <access_token>`
- Path Parameters:
  - `id` (UUID, required)
- Request Body: None

### 2.3 POST /expenses
- HTTP Method: POST
- URL: `/expenses`
- Headers:
  - `Authorization: Bearer <access_token>`
- Request Body (JSON, mapped to `ExpenseCreate`):
  ```json
  {
    "amount": 12.50,
    "description": "Lunch",
    "category_id": "uuid"  // optional
  }
  ```

### 2.4 PUT /expenses/{id}
- HTTP Method: PUT
- URL: `/expenses/{id}`
- Headers:
  - `Authorization: Bearer <access_token>`
- Path Parameters:
  - `id` (UUID, required)
- Request Body (JSON, mapped to `ExpenseUpdate`): same structure as POST

### 2.5 DELETE /expenses/{id}
- HTTP Method: DELETE
- URL: `/expenses/{id}`
- Headers:
  - `Authorization: Bearer <access_token>`
- Path Parameters:
  - `id` (UUID, required)
- Request Body: None

### 2.6 GET /expenses/summary
- HTTP Method: GET
- URL: `/expenses/summary`
- Headers:
  - `Authorization: Bearer <access_token>`
- Query Parameters:
  - `period` (string, required, e.g., `weekly`)
- Request Body: None

## 3. Response Details

### 3.1 GET /expenses
- Status: 200 OK
- Body (mapped to `ExpenseList`):
  ```json
  {
    "data": [ /* ExpenseRead objects */ ],
    "pagination": { "limit": 20, "offset": 0, "total": 150 }
  }
  ```
- Models: `ExpenseRead`, `Pagination`, `ExpenseList`

### 3.2 GET /expenses/{id}
- Status: 200 OK
- Body: `ExpenseRead`
- Errors: 404 Not Found

### 3.3 POST /expenses
- Status: 201 Created
- Body: `ExpenseRead`
- Errors: 400 Bad Request

### 3.4 PUT /expenses/{id}
- Status: 200 OK
- Body: `ExpenseRead`
- Errors: 400 Bad Request, 404 Not Found

### 3.5 DELETE /expenses/{id}
- Status: 204 No Content
- Errors: 404 Not Found

### 3.6 GET /expenses/summary
- Status: 200 OK
- Body: `ExpenseSummary`
- Errors: 400 Bad Request (invalid `period`)

## 4. Data Flow
1. **Authentication**: JWT middleware validates token, extracts `user_id`.
2. **Routing**: `expenses_bp` Flask Blueprint maps HTTP requests to controller functions.
3. **Controller**:
   - Parses path, query, and body parameters using Pydantic models.
   - Handles validation errors and returns 400 if necessary.
   - Invokes corresponding methods on `ExpenseService`.
4. **Service Layer (`ExpenseService`)**:
   - `list_expenses(user_id, filters)` ↦ SELECT with RLS, pagination, filtering.
   - `get_expense(user_id, expense_id)` ↦ SELECT one record or raise NotFound.
   - `create_expense(user_id, dto: ExpenseCreate)` ↦ INSERT, assign default category if missing.
   - `update_expense(user_id, expense_id, dto: ExpenseUpdate)` ↦ UPDATE or raise NotFound.
   - `delete_expense(user_id, expense_id)` ↦ DELETE or raise NotFound.
   - `get_summary(user_id, period)` ↦ aggregated SELECT with date truncation.
5. **Database**: Supabase client executes parameterized queries; RLS ensures correct user scope.
6. **Logging**: On create/update/delete, insert a `logs` record with type `info` or `error` on failure.
7. **Response**: Controller serializes DTOs to JSON and returns appropriate HTTP status.

## 5. Security Considerations
- **JWT Authentication**: Reject unauthorized requests with 401.
- **Row Level Security (RLS)**: Enforce `user_id = auth.uid()` for all table operations.
- **Input Validation**: Pydantic models enforce type constraints and limit field lengths.
- **SQL Injection Prevention**: Use parameterized queries via Supabase client.
- **Rate Limiting**: (If needed) apply per-user limits on expensive operations.
- **CORS**: Restrict origins to trusted frontend domains.

## 6. Error Handling
| HTTP Status | Condition                                         | Action                                         |
|-------------|---------------------------------------------------|------------------------------------------------|
| 200         | Success for GET, PUT                             | Return DTO and payload                         |
| 201         | Success for POST                                  | Return created DTO                             |
| 204         | Success for DELETE                                | Return no content                              |
| 400         | Validation error (Pydantic failure, invalid input)| Return JSON with error details                 |
| 401         | Missing or invalid JWT                            | Return 401 Unauthorized                        |
| 404         | Resource not found                                | Return 404 Not Found                           |
| 500         | Database or server error                          | Log error, return 500 Internal Server Error    |

## 7. Performance Considerations
- **Index Utilization**: Ensure use of `idx_expenses_user_date` and `idx_expenses_user_amount`.
- **Pagination Strategy**: Offset-limit pagination; consider cursor-based if performance issues arise.
- **Selective Fields**: Only select required columns to reduce payload size.
- **Caching**: Implement caching for summary endpoint if needed.
- **Query Optimization**: Use proper WHERE clauses and avoid unnecessary JOINs.

## 8. Implementation Steps
1. **Blueprint & Routing**: Create `expenses_bp` Flask Blueprint and register endpoints.
2. **Authentication Middleware**: Configure JWT validation (e.g., `flask-jwt-extended`).
3. **DTOs & Schemas**: Verify or add `ExpenseCreate`, `ExpenseUpdate`, `ExpenseRead`, `Pagination`, `ExpenseList`, `ExpenseSummary` in `schemas.py`.
4. **Service Layer**: Implement `ExpenseService` with methods: `list_expenses`, `get_expense`, `create_expense`, `update_expense`, `delete_expense`, `get_summary`.
5. **Controllers**: Develop controller functions in `app/controllers/expenses.py`, map request to service, handle exceptions.
6. **Database Integration**: Configure Supabase client for Python, ensure RLS policies in place.
7. **Logging**: Create log entries in `logs` table for create/update/delete operations.
8. **Unit & Integration Tests**: Write tests for service methods and endpoint behavior.
9. **API Documentation**: Update OpenAPI/Swagger definitions for all `/expenses` routes.
10. **Code Review & QA**: Perform code review, manual testing, and deploy to staging environment.
11. **Deployment**: Merge to main branch, run CI/CD pipeline, and deploy to production. 