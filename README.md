# Spending Frustration

Spending Frustration is an experimental personal finance categorization monolith. It lets a user:

1. Register & authenticate (JWT based)
2. Store & retrieve transactions
3. Define rules composed of conditions + actions (future: apply them automatically)
4. (Planned) Upload bank / card statement CSV files for ingestion

Technologies: FastAPI (Python), MongoDB, React (TypeScript – scaffold stage).

## High-Level Goals
- Keep architecture intentionally simple (no service layer yet)
- Expose raw Mongo `_id` in responses for transparency
- Make rule system extensible for later enrichment & automation
- Provide clear, AI-friendly documentation for future iteration

## Repository Layout
| Path | Description |
|------|-------------|
| `backend/` | FastAPI backend application |
| `frontend/` | React frontend scaffold |
| `docs/` | In-depth technical documentation |

## Getting Started (Backend Quickstart)
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

Set `MONGO_URI` and (optional) `MONGO_DB` env vars. Replace `SECRET_KEY` in `backend/app/auth.py` before any non-local use.

## Documentation
Detailed docs live in the `docs/` folder:
- API surface: `docs/api-endpoints.md`
- Database models: `docs/database-models.md`
- Architecture decisions: `docs/architecture.md`
- Glossary: `docs/glossary.md`
- AI context guide: `docs/ai-prompt-notes.md`

## Roadmap (Short-Term)
- Rule execution engine to auto-categorize
- Indexing & performance tuning
- Frontend UI build-out
- Rule application audit trail

## Frontend (Refactor Overview)
The React (Vite + TypeScript) frontend now includes minimal, focused components:

| Component | Purpose |
|-----------|---------|
| `NavBar` | Simple in-memory navigation between feature views (no router yet) |
| `Transactions` | Lists transactions with basic filtering (merchant/category/tags/amount). Can optionally hit server filter endpoint. |
| `RulesManager` | CRUD interface for textual rules (each rule is a single string; name + active flag) |
| `api.ts` | Tiny fetch helper that injects `Authorization: Bearer <token>` if `localStorage.authToken` exists |

Run it:
```sh
cd frontend
npm install
npm run dev
```
Optionally create `frontend/.env` with `VITE_API_BASE=http://localhost:8000`.

### Authentication Flow (Frontend)
1. Start the backend (see quickstart above).
2. Visit the frontend dev server (default: http://localhost:5173).
3. You'll see a login/register card. First-time: switch to Register, enter username + password (email optional), submit.
4. On success, switch to Login automatically; enter credentials and login. A JWT is stored in `localStorage.authToken`.
5. After login, the app shows navigation (Transactions / Rules). All API calls now include `Authorization: Bearer <token>`.
6. Use the Logout button (top-right) to clear the token and return to the auth screen.

The token is not auto-refreshed; for now you may need to re-login after expiry (24h default). Replace the hard-coded `SECRET_KEY` in `backend/app/auth.py` before any multi-user scenario.

### Rule Creation Notes
- New textual rules are appended at the end of your rule list automatically (priority = current count).
- You can optionally supply a `priority` integer in the POST body to insert at a specific index.
- Backend accepts omission of `priority` and will compute the next index.

Rules are currently stored as plain text lines (see `UserRules` and `RuleDB` models) and parsed server-side. The UI edits the raw rule string; advanced structured editing is postponed.

Planned UI enhancements (not yet implemented): pagination, routing (React Router), optimistic updates, validation & toast notifications, multi-condition visual builder.


## 📋 License

This project is licensed under the **Functional Source License (FSL) 1.1** - see the [LICENSE](LICENSE) file for full details.

### What does this mean?

#### ✅ You CAN:
- **Use it personally** - Run it on your Raspberry Pi, home server, or personal computer
- **Modify the code** - Fork it, customize it, adapt it to your needs
- **Use it internally** - Deploy it within your organization for internal business use
- **Study and learn** - Examine the code to understand how it works
- **Share modifications** - Contribute improvements back to the project
- **Use it non-commercially** - Run it for educational, research, or hobby projects

#### ❌ You CANNOT:
- **Offer it as a service** - You may not make the functionality available to third parties as a service (free or paid)
- **Host it publicly** - You cannot deploy this for others to use, even if you don't charge for it
- **Compete with our SaaS** - This includes offering free alternatives that compete with our commercial offering
- **Remove license notices** - Keep all copyright and license information intact

### Why this license?

We want to keep this project **source-available** so you can learn from it, self-host it, and use it freely for personal and internal purposes. However, we operate a commercial SaaS version at [your-domain.com], and this license protects our ability to sustain development while keeping the code transparent.

The key restriction is simple: **you can use it yourself, but you can't offer it to others as a service.**

### Self-Hosting

You're welcome to self-host this application for:
- ✅ Personal use at home
- ✅ Internal use within your organization/company
- ✅ Development and testing purposes
- ✅ Educational and research purposes
- ❌ Providing access to third parties (employees using it internally is fine, external users is not)

### Examples

**Allowed:**
- Installing it on your home server for your family
- Deploying it at your company for your employees
- Running it on your laptop for personal projects
- Using it for your university research

**Not Allowed:**
- Hosting it on a public website for anyone to use
- Offering it as a free alternative to our paid service
- Running it as a community service for external users
- Providing it to your clients or customers

---

## 📧 Contact

For questions about licensing or commercial use, reach out to stanislav.alexovic@gmail.com.

For technical support and bug reports, please go to [github issues](https://github.com/elanius/spending-frustration/issues).

---

**Note**: This software is source-available with usage restrictions. While you can view, modify, and self-host the code, offering it as a service to third parties (free or paid) is prohibited.
