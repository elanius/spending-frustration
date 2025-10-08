# Glossary & Domain Concepts

| Term | Definition |
|------|------------|
| Transaction | A single financial record representing money spent or received. |
| Category | A high-level classification label assigned to a transaction (e.g., `food_drink`). |
| Tag | A free-form user-defined label for faceted filtering (e.g., `coffee`, `work`). |
| Rule | A user-defined conditional definition that can assign category/tags to matching transactions. |
| Condition | Part of a rule specifying a field, an operator, and a value. |
| Action | The outcome of a rule (category/tags to set). |
| Logical Operator | Determines how multiple conditions inside a rule combine (`AND` / `OR`). |
| Merchant | Vendor or payee descriptor extracted from the original source statement. |
| Ingestion | Future process of importing transactions from CSV or other external sources. |
| Normalization | Converting free-form input (tags, merchants) into consistent stored forms. |

## Naming Conventions
- All Python variable names use snake_case.
- HTTP paths are lowercase with hyphens only when needed (current: none besides potential `/upload-statement`).
- Mongo collections: `users`, `transactions`, `rules`.

## ObjectId Usage
- Exposed as `_id` in responses for transparency.
- Never mutated client-side; treated as opaque identifiers.

## Tag Handling
- Input can be comma-separated string or JSON array (router normalizes to list).
- Duplicate/empty entries discarded.

## Categories vs Tags
- Category: one per transaction (replace existing on update).
- Tags: multiple allowed (current patch replaces entire list; future enhancement could merge).
