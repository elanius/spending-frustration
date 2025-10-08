# Database Models

This document describes MongoDB document structures used in the application. These are raw storage models (not the Pydantic request/response schemas used at the API layer).

## Conventions
- `_id` is always a MongoDB ObjectId.
- `user_id` references the owning user's `_id`.
- Arrays default to absence (field omitted) or empty list depending on write context.
- API layer performs validation; DB layer stores already-normalized data.

## User Collection (`users`)
| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | Primary key |
| `email` | string (EmailStr) | Unique per user |
| `hashed_password` | string | Bcrypt hash |

Example:
```json
{
  "_id": "64f0c2...",
  "email": "user@example.com",
  "hashed_password": "$2b$12$..."
}
```

## Transactions Collection (`transactions`)
| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | Primary key |
| `user_id` | ObjectId | FK to users `_id` |
| `date` | ISODate | UTC timestamp of transaction (at day precision currently) |
| `amount` | number | Positive or negative; sign indicates direction (expense negative optional future) |
| `merchant` | string | Raw or cleaned merchant descriptor |
| `category` | string (optional) | Assigned category label |
| `tags` | array[string] (optional) | Normalized lowercase tags (router ensures trimming) |
| `notes` | string (optional) | Free-form annotation |

Example:
```json
{
  "_id": "6500be...",
  "user_id": "64f0c2...",
  "date": "2025-09-01T00:00:00Z",
  "amount": 42.15,
  "merchant": "Coffee Roasters",
  "category": "food_drink",
  "tags": ["coffee", "morning"],
  "notes": "Team sync latte"
}
```

## Rules Collection (`rules`)
| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | Primary key |
| `user_id` | ObjectId | FK to users `_id` |
| `conditions` | array[Condition] | Evaluated sequentially with logical operator |
| `logical_operator` | string | `AND` or `OR` |
| `priority` | int >= 0 | Higher precedence when applying rules (larger number wins) |
| `action` | object | Category/tags assignment payload |

### Condition Object
| Field | Type | Notes |
|-------|------|-------|
| `field` | string | e.g. `merchant`, `amount`, `category` |
| `operator` | string | Future: `contains`, `eq`, `regex`, `gt`, `lt` |
| `value` | any | Comparison target |

### Action Object
| Field | Type | Notes |
|-------|------|-------|
| `category` | string (optional) | Category to set |
| `tags` | array[string] (optional) | Tags to merge / set (current behavior: replace) |

Example:
```json
{
  "_id": "6500c1...",
  "user_id": "64f0c2...",
  "conditions": [
    {"field": "merchant", "operator": "contains", "value": "coffee"}
  ],
  "logical_operator": "AND",
  "priority": 10,
  "action": {"category": "food_drink", "tags": ["coffee"]}
}
```

## Future Extensions
- Add `created_at`, `updated_at` audit fields.
- Normalize merchant names into separate collection for analytics.
- Add rule execution history collection for debugging.
