# AI Tips API Endpoint

## Description

The `/ai/tips` endpoint delivers personalized, AI-generated financial tips to an authenticated user. These tips are based on the user's historical expense data, highlighting spending trends, flagging unusual transactions, and suggesting budgeting or savings strategies.

## Endpoint Details

- **URL**: `/ai/tips`
- **Method**: `GET`
- **Authentication**: Required (Bearer token)

## Request Parameters

| Parameter | Type    | Required | Default | Description                        |
|-----------|---------|----------|---------|------------------------------------|
| limit     | integer | No       | 3       | Maximum number of tips to return (1-3) |

## Response Format

### Success Response (200 OK)

```json
[
  {
    "message": "Your dining out expenses increased by 20% this week. Try cooking at home to save."
  },
  {
    "message": "Entertainment spending is trending higher than usual. Consider setting a monthly limit."
  },
  {
    "message": "You've been consistent with grocery spending. Great job keeping to your budget!"
  }
]
```

### Error Responses

#### 400 Bad Request
Invalid `limit` parameter (not an integer, less than 1, or greater than 3)

```json
{
  "error": "Invalid limit parameter",
  "message": "Limit must be between 1 and 3"
}
```

#### 401 Unauthorized
Missing or invalid authentication token

```json
{
  "error": "Authentication required"
}
```

#### 502 Bad Gateway
AI service timeout or failure

```json
{
  "error": "External AI service unavailable",
  "message": "AI service error after maximum retries"
}
```

#### 500 Internal Server Error
Unexpected server error

```json
{
  "error": "Internal server error"
}
```

## Example Usage

### cURL

```bash
curl -X GET "https://api.example.com/ai/tips?limit=2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### JavaScript

```javascript
const getTips = async () => {
  try {
    const response = await fetch('https://api.example.com/ai/tips?limit=2', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    const tips = await response.json();
    return tips;
  } catch (error) {
    console.error('Failed to fetch tips:', error);
  }
};
```

### Python

```python
import requests

def get_tips(access_token, limit=3):
    url = "https://api.example.com/ai/tips"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "limit": limit
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raise exception for 4XX/5XX responses
    
    return response.json()
```

## Notes

- The endpoint uses the OpenRouter.ai API to generate tips based on the user's expense data.
- Tips are generated based on the most recent 2 weeks of the user's expense data.
- If the user has no expenses, the endpoint will return general financial tips for beginners.
- The response will always contain at least one tip, even in case of errors with the AI service. 