# Architecture & Design Decisions

## Overview
Spending Frustration is a monolithic application composed of:
- FastAPI backend (Python) — authentication, rules engine scaffolding, transaction management
- React frontend (TypeScript) — (scaffold placeholder currently)
- MongoDB — document storage (users, transactions, rules)

## Guiding Principles
- KISS & clarity over abstraction
- Avoid premature layering (no service/repository indirection yet)
- Keep raw Mongo `_id` fields in API responses for transparency
- Separate DB document models (`models.py`) from API schemas (defined per-router)
- Prefer explicit descriptive names (no single-letter variables)

## Module Layout
| Path | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app factory + router registration |
| `backend/app/auth.py` | JWT + password hashing utilities and current user dependency |
| `backend/app/db.py` | Mongo client & base collection handles |
| `backend/app/models.py` | DB document Pydantic models (DBUser, DBTransaction, DBRule) |
| `backend/app/routers/auth.py` | Register/login endpoints |
| `backend/app/routers/rules.py` | Rule CRUD with inline schema validation |
| `backend/app/routers/transactions.py` | Transaction list/get/patch/filter |
| `backend/app/routers/upload.py` | Placeholder for future CSV ingestion |

## Authentication
- JWT (HS256) with configurable expiry (`ACCESS_TOKEN_EXPIRE_MINUTES`)
- OAuth2PasswordBearer dependency for protected endpoints
- Passwords hashed with bcrypt (passlib)

## Data Flow (Example: PATCH Transaction)
1. Request hits `/transactions/{tx_id}` with JSON body
2. Router-level `TransactionPatch` schema validates/normalizes tags
3. Mongo update operation performs `$set` with filtered non-null fields
4. Response: simple message or serialized document (depending on endpoint)

## Rules Engine (Current State)
- Stores user-defined rules with conditions + action
- Not yet applied automatically — future planned: batch processing & live ingestion hook

## Error Handling
- Minimal custom exceptions — rely on FastAPI `HTTPException`
- Validation errors surfaced automatically via Pydantic

## Performance Considerations
- Current queries rely on implicit collection scans; indexes to add soon:
  - `transactions: { user_id: 1, date: -1 }`
  - `rules: { user_id: 1, priority: -1 }`
  - `users: { email: 1 } (unique)`

## Future Enhancements
- Central rule application service with dry-run mode
- Background tasks for re-categorization
- Bulk CSV normalization & enrichment pipeline
- Tag/category analytics aggregation
- Frontend integration & static build serving from FastAPI

## Trade-offs
| Decision | Rationale | Consequence |
|----------|-----------|-------------|
| Monolith | Simple deploy | Less isolation between concerns |
| Inline router schemas | Reduced coupling | Some duplication risk later |
| Raw `_id` exposure | Debug clarity | Client must treat as opaque |
| No service layer yet | Speed | Harder to unit test in depth later |

## Security Notes
- SECRET_KEY placeholder must be replaced in production
- Add rate limiting & audit logging in future
- Consider refresh tokens for long-lived sessions
