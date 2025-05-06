# API Endpoint Implementation Plan: GET /ai/tips

## 1. Endpoint Overview
The `GET /ai/tips` endpoint delivers up to three personalized, AI-generated financial tips to an authenticated user within a single session. Leveraging the user's historical expense data, it provides actionable insights—highlighting spending trends, flagging unusual transactions, and suggesting budgeting or savings strategies. These tips can be displayed in the application's dashboard, notifications, or a dedicated tips panel to help users better understand their financial habits and make informed decisions. Session-based tracking ensures that each user receives a limited number of tips per session, balancing user experience with external AI service costs and preventing overuse.

## 2. Request Details
- HTTP Method: GET
- URL Pattern: `/ai/tips`
- Query Parameters:
  - Required: _none_ (besides authentication)
  - Optional:
    - `limit` (integer, default: 3, maximum: 3) – the maximum number of tips to return
- Headers:
  - `Authorization: Bearer <access_token>`

## 3. Response Structure

### DTOs and Command Models
- **AiTip** (defined in `app/schemas.py`):
  ```python
  class AiTip(BaseModel):
      message: str
  ```

### Successful Response
- **200 OK**
  ```json
  [
    { "message": "Your dining out expenses increased by 20% this week. Try cooking at home to save." },
    { "message": "Entertainment spending is trending higher than usual. Consider setting a monthly limit." }
  ]
  ```

### Error Responses
- **400 Bad Request** – invalid `limit` value (not an integer, less than 1, or greater than 3)
- **401 Unauthorized** – missing or invalid authentication token
- **502 Bad Gateway** – AI service timeout or failure
- **500 Internal Server Error** – unexpected server error

## 4. Data Flow
1. Authentication middleware validates the Supabase JWT from the `Authorization` header and extracts `user_id`.
2. The Flask route handler parses and validates the `limit` parameter (int between 1 and 3, defaulting to 3).
3. The handler calls `AiTipsService.get_tips(user_id, limit)`:
   - Optionally checks session or cache to track how many tips were already delivered.
   - Builds an AI prompt using the user's recent expense patterns.
   - Sends a request to the Openrouter.ai API with a 10-second timeout and up to 3 retries.
   - Maps the AI response to a list of `AiTip` instances.
4. The handler serializes the `AiTip` list and returns it as a JSON response.

## 5. Security Considerations
- **Authentication & Authorization**: Enforce Supabase JWT; use PostgreSQL RLS to restrict data access to the authenticated user.
- **Rate Limiting**: Restrict to 5 calls per minute per user (e.g., Flask-Limiter).
- **Input Validation**: Sanitize and clamp the `limit` parameter.
- **CORS**: Allow only trusted frontend origins.
- **Transport Security**: Use HTTPS for all external API calls.

## 6. Error Handling
| HTTP Status | Condition                                         | Action & Logging                                                                                       |
|-------------|----------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| 400         | `limit` parameter out of range or invalid type      | `abort(400, 'Invalid limit parameter')`                                                                |
| 401         | Missing or invalid token                            | `abort(401)`                                                                                           |
| 502         | AI service timeout or error                         | Log to `logs` table with `type='error'`, `error_code='AI_TIMEOUT'` or `AI_ERROR`, return 502           |
| 500         | Unexpected server exception                         | Log to `logs` table with `type='error'`, `error_code='SERVER_ERROR'`, return 500                       |

> **Error Logging**: For 502 and 500 errors, insert a record in `logs` with:
> - `user_id`, `type='error'`, `error_code`, `message` (exception details), `created_at`.

## 7. Performance Considerations
- **Caching**: Cache generated tips in session store or Redis to reduce redundant AI calls.
- **HTTP Connection Pooling**: Reuse connections for Openrouter.ai requests.
- **Asynchronous Processing**: Consider async calls (if framework supports) to improve throughput.
- **Monitoring & Metrics**: Track call counts, latency, and error rates (e.g., via Prometheus).

## 8. Implementation Steps
1. Create `app/api/ai_tips.py` and register a Flask Blueprint `ai_tips_bp`.
2. Define the route:
   ```python
   @ai_tips_bp.route('/tips', methods=['GET'])
   @requires_auth
   def get_ai_tips():
       ...
   ```
3. Parse and validate the `limit` parameter (using Pydantic or manual validation).
4. Implement `AiTipsService` in `app/services/ai_tips_service.py` with method `get_tips(user_id: UUID, limit: int) -> List[AiTip]`.
5. In `AiTipsService`, call the Openrouter.ai API with retry logic and timeout handling.
6. Apply rate limiting to the endpoint (e.g., with Flask-Limiter).
7. Handle AI service errors and log failures via a `LogRepository`.
8. Serialize `AiTip` instances and return as JSON (Flask + `jsonify`).
9. Write unit and integration tests (mock Openrouter.ai, test authentication and input validation).
10. Update API documentation (README / Swagger) with examples.
11. Add CI pipeline steps (linting, testing) and deploy to staging.
12. Perform manual acceptance testing and monitor production metrics post-deployment. 