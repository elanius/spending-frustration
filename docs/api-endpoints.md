# API Endpoints

Base URL: `/` (monolith). All protected endpoints require Bearer JWT from `/auth/login`.

## Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create user (email + password) |
| POST | `/auth/login` | No | Obtain JWT access token |

### POST `/auth/register`
Request JSON:
```json
{ "email": "user@example.com", "password": "Secret123!" }
```
Response 201:
```json
{ "message": "User created", "user_id": "<object_id>" }
```

### POST `/auth/login`
Request form-data (OAuth2PasswordRequestForm compatible):
```
username=<email>
password=<password>
```
Response 200:
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

## Rules
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/rules` | Yes | List rules sorted by priority desc |
| POST | `/rules` | Yes | Create new rule |
| GET | `/rules/{rule_id}` | Yes | Retrieve rule by id |
| PUT | `/rules/{rule_id}` | Yes | Update entire rule (partial allowed via nullable fields) |
| DELETE | `/rules/{rule_id}` | Yes | Delete rule |

Rule create/update payload shape (simplified):
```json
{
  "conditions": [{"field": "merchant", "operator": "contains", "value": "coffee"}],
  "logical_operator": "AND",
  "priority": 5,
  "action": {"category": "food_drink", "tags": ["coffee"]}
}
```

## Transactions
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/transactions` | Yes | Paginated list (page, limit, optional sort=field:asc|desc) |
| GET | `/transactions/{tx_id}` | Yes | Get single transaction |
| PATCH | `/transactions/{tx_id}` | Yes | Partial update (category, tags, notes) |
| GET | `/transactions/filter` | Yes | Flexible filtering |

Filter query params:
- `date_from`, `date_to` (ISO timestamps)
- `category`
- `tags` (comma separated; all required)
- `amount_min`, `amount_max`
- `merchant_contains`

Response item shape:
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

## Upload
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/upload-statement` | Yes | Upload CSV bank/export and insert transactions |

Accepted columns (header, case-sensitive):
- Required: `date`, `amount`, `merchant`
- Optional: `category`, `tags`, `notes`

Example CSV:
```
date,amount,merchant,category,tags,notes
2025-09-01,42.15,Coffee Roasters,food_drink,"coffee,morning",Team sync latte
2025-09-02,12.00,Sandwich Shop,food_drink,lunch,
```

Response 200:
```json
{
  "inserted": 2,
  "skipped": 0,
  "unexpected_columns": [],
  "sample": [ { "user_id": "<id>", "date": "2025-09-01 00:00:00", "amount": 42.15, "merchant": "Coffee Roasters", "category": "food_drink", "tags": ["coffee","morning"], "notes": "Team sync latte", "_id": "<id>" } ],
  "errors": []
}
```

Error rows (e.g., bad date / missing amount) appear in `errors` with `row_index` and `raw`.

## Error Model
Errors follow FastAPI default:
```json
{ "detail": "<message>" }
```

## Future Additions
- Rule execution endpoint to apply categorization retrospectively
- Bulk tag assignment
- CSV template generation
