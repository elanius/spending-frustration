# AI Prompt Notes

This file helps future AI-assisted development sessions load concise, high-signal context.

## Core Summary
Spending Frustration is a FastAPI + Mongo monolith for managing personal spending. Users authenticate (JWT), create rules to categorize transactions, and view/modify transactions. CSV upload + rule execution pipeline are planned but not yet implemented.

## Key Entities
- User: email + hashed_password
- Transaction: date, amount, merchant, optional category, tags, notes
- Rule: conditions[] + logical_operator + priority + action{category,tags}

## Architectural Constraints
- No service/repository abstraction yet — routers talk directly to MongoDB collections.
- DB-only models in `models.py`; API Pydantic schemas live inside each router file.
- Raw Mongo `_id` preserved in responses.
- Descriptive variable names enforced (no single-letter identifiers).

## Pending / TODO (as of last update)
- Implement `/upload-statement` endpoint (CSV ingestion)
- Register additional routers in `main.py` (rules, transactions, upload placeholder)
- Add indexing migration notes
- Apply rules to transactions automatically

## Common Extension Patterns
- Add new endpoint: create router file or extend existing, define inline Pydantic models, include router in `main.py`.
- Add new field to collection: update `DB*` model in `models.py`, adapt router schemas, write migration/backfill script if needed.

## Security & Ops
- Replace `SECRET_KEY` before production deploy.
- Add rate limiting + logging later.

## Example Prompt Template
"You are working on Spending Frustration (FastAPI + Mongo) with existing entities: User, Transaction, Rule. Database models are in backend/app/models.py; API schemas defined inline per router. No service layer. Implement <feature> ensuring raw _id fields remain in responses and follow existing naming/validation conventions."

## Retrieval Tips
If context token budget is limited, prioritize in this order:
1. `architecture.md`
2. `api-endpoints.md`
3. `database-models.md`
4. `glossary.md`

