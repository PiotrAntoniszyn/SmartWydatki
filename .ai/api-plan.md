# REST API Plan

## 1. Resources

- **Authentication** (Supabase Auth managing `users`)
- **Users** (`users` table)
- **Categories** (`categories` table)
- **Expenses** (`expenses` table)
- **Category Suggestions** (AI-powered suggestions)
- **Weekly Summary** (`expenses/summary` aggregated data)
- **AI Tips** (financial advice)
- **Logs** (`logs` table; internal use)

## 2. Endpoints

### 2.1 Categories

**GET /categories**
- Description: List all categories for current user.
- Query Params: none
- Headers: `Authorization: Bearer <access_token>`
- Response 200 OK:
  ```json
  [
    { "id": "uuid", "name": "Food", "is_default": false },
    { "id": "uuid", "name": "Uncategorized", "is_default": true }
  ]
  ```

**POST /categories**
- Description: Create a new category.
- Request Body:
  ```json
  { "name": "Transport" }
  ```
- Response 201 Created:
  ```json
  { "id": "uuid", "name": "Transport", "is_default": false }
  ```
- Errors:
  - 400 Bad Request (name > 30 chars)
  - 409 Conflict (duplicate name)

**GET /categories/:id**
- Description: Retrieve a single category.
- Response 200 OK: Category object
- Errors: 404 Not Found

**PUT /categories/:id**
- Description: Update category name.
- Request Body: `{ "name": "Groceries" }`
- Response 200 OK: Updated category
- Errors: 400, 404, 409

**DELETE /categories/:id**
- Description: Delete a non-default category.
- Response 204 No Content
- Errors: 400 Bad Request (attempt to delete default), 404 Not Found

**GET /categories/suggestions**
- Description: Return up to 3 AI-powered category suggestions sorted by usage.
- Query Params:
  - `description` (string)
  - `amount` (number)
- Response 200 OK:
  ```json
  [
    { "id": "uuid", "name": "Coffee", "usage_count": 15 },
    { "id": "uuid", "name": "Snacks", "usage_count": 5 }
  ]
  ```
- Errors: 502 Bad Gateway (AI timeout/error)

### 2.2 Expenses

**GET /expenses**
- Description: Get paginated list of expenses.
- Query Params:
  - `limit` (int, default 20)
  - `offset` (int, default 0)
  - `search` (string, description filter)
  - `date_from` (ISO date)
  - `date_to` (ISO date)
  - `amount_min` (number)
  - `amount_max` (number)
- Response 200 OK:
  ```json
  {
    "data": [ { /* expense */ } ],
    "pagination": { "limit": 20, "offset": 0, "total": 150 }
  }
  ```

**GET /expenses/:id**
- Description: Retrieve a single expense.
- Response 200 OK: Expense object
- Errors: 404 Not Found

**POST /expenses**
- Description: Create a new expense.
- Request Body:
  ```json
  {
    "amount": 12.50,
    "description": "Lunch",
    "category_id": "uuid" // optional
  }
  ```
- Response 201 Created: Expense object
- Errors: 400 Bad Request (validation)

**PUT /expenses/:id**
- Description: Update an expense (no AI re-categorization).
- Request Body: same as POST
- Response 200 OK: Updated expense
- Errors: 400, 404

**DELETE /expenses/:id**
- Description: Delete an expense.
- Response 204 No Content
- Errors: 404 Not Found

**GET /expenses/summary**
- Description: Weekly summary of expenses.
- Query Params: `period=weekly`
- Response 200 OK:
  ```json
  { "total_amount": 250.00, "transaction_count": 20 }
  ```

### 2.3 AI Tips

**GET /ai/tips**
- Description: Get up to 3 financial advice messages per session.
- Query Params:
  - `limit` (int, default 3)
- Response 200 OK:
  ```json
  [ { "message": "You spent more than usual on coffee this week." } ]
  ```
- Errors: 502 Bad Gateway

### 2.4 Logs (Internal)

**GET /logs**
- Description: Retrieve operation logs for debugging or audit.
- Query Params: `limit`, `offset`
- Response 200 OK: Array of log entries

## 3. Authentication & Authorization

- Use Supabase JWT tokens in `Authorization: Bearer <token>` header.
- Row-Level Security (RLS) policies enforce `user_id = auth.uid()` on all tables.
- Only authenticated users can access resources (HTTP 401 otherwise).

## 4. Validation & Business Logic

### 4.1 Validation Rules
- **User**: email format, password ≥ 8 chars.
- **Category**: name ≤ 30 chars, unique per user, cannot delete default.
- **Expense**: amount > 0, max 2 decimal places, description ≤ 100 chars, defaults to user's "Uncategorized" category via `get_default_category_id()`.
- **Logs**: capture type (`info|warning|error`), optional `error_code`, and `message`.

### 4.2 Business Logic Implementation
- **Default Category Creation**: Triggered after registration via DB trigger (`trg_create_default_category`).
- **Pagination & Sorting**: `GET /expenses` ordered by `date_of_expense DESC`, leveraging `idx_expenses_user_date` index.
- **Filtering & Searching**: Apply SQL WHERE clauses on `description ILIKE`, `date_of_expense` range, and `amount` range.
- **AI Integration**: External API calls with 10s timeout and 3 retries. Errors return 502 with retry option.
- **Logging**: Middleware records create/update/delete operations to `logs` table using `info` for success or `error` for failures.

### 4.3 Security & Performance
- Rate limit AI endpoints (e.g., 5 req/min per user).
- CORS restricted to our frontend domain.
- Inputs sanitized to prevent SQL injection (use parameterized queries).
- Supabase RLS ensures horizontal data isolation per user.
- Use appropriate DB indexes (`idx_categories_user_default`, `idx_expenses_user_amount`, `idx_logs_user_created_at`).

---
*This plan aligns with the given database schema, PRD requirements, and the Python/Flask + Supabase tech stack.* 