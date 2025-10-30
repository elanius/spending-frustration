// Minimal API client helper
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function authHeader(): Record<string, string> {
    const token = localStorage.getItem("authToken");
    return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handle<T>(res: Response): Promise<T> {
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed (${res.status})`);
    }
    return res.json();
}

export const api = {
    get: <T>(path: string, params?: Record<string, any>) => {
        const url = new URL(path, API_BASE);
        if (params) {
            Object.entries(params).forEach(([k, v]) => {
                if (v === undefined || v === null || v === "") return;
                url.searchParams.append(k, String(v));
            });
        }
        const headers: Record<string, string> = { ...authHeader() };
        return fetch(url.toString(), { headers }).then(handle<T>);
    },
    post: <T>(path: string, body: any) =>
        fetch(`${API_BASE}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json", ...authHeader() } as Record<string, string>,
            body: JSON.stringify(body),
        }).then(handle<T>),
    put: <T>(path: string, body: any) =>
        fetch(`${API_BASE}${path}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json", ...authHeader() } as Record<string, string>,
            body: JSON.stringify(body),
        }).then(handle<T>),
    delete: (path: string) =>
        fetch(`${API_BASE}${path}`, {
            method: "DELETE",
            headers: { ...authHeader() } as Record<string, string>,
        }).then(handle<{ message: string }>),
    login: async (username: string, password: string) => {
        const form = new URLSearchParams();
        form.append("username", username);
        form.append("password", password);
        // OAuth2 spec requires grant_type but FastAPI's default OAuth2PasswordRequestForm expects username/password only
        return fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: form.toString(),
        }).then(handle<Token>);
    },
    register: async (username: string, password: string, email?: string) => {
        return fetch(`${API_BASE}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password, email }),
        }).then(handle<{ message: string; user_id: string }>);
    },
};

// Types
export interface Transaction {
    id: string; // _id alias
    _id?: string; // in case backend returns _id
    // ISO date string
    date: string;
    amount: number;
    // transaction type e.g. "card_payment", "transfer"
    transaction_type?: string | null;
    // asset and counterparty follow backend models: counterparty may contain merchant, bank or wallet
    counterparty?: {
        merchant?: { name: string } | null;
        bank?: { account_name?: string | null; iban?: string | null; bic?: string | null } | null;
        wallet?: { wallet_name?: string | null } | null;
    } | null;
    // human-friendly description/note
    description?: string | null;
    // some backends use `note` or `notes`
    note?: string | null;
    notes?: string | null;
    category?: string | null;
    tags?: string[] | null;
    // details object containing additional metadata
    details?: {
        message_for_recipient?: string | null;
        transaction_note?: string | null;
        balance?: number | null;
        currency?: string | null;
        operation_type?: string | null;
        location?: string | null;
        symbols?: Record<string, string> | null;
    } | null;
}

export interface Condition {
    field: string;
    operator: string; // e.g., EQUALS, CONTAINS
    value: string | number | boolean;
}

export interface Action {
    type: string; // minimal for now
    field?: string;
    value?: string;
}

// Textual rule model (backend stored in single document user_rules)
export interface TextRule {
    id: string;
    rule: string; // full textual rule e.g. "merchant contains Coffee -> @coffee #caffeinated"
    active: boolean;
}

export interface TextRuleCreateInput {
    rule: string;
    active?: boolean; // default true
}

export interface TextRuleUpdateInput {
    rule?: string;
    active?: boolean;
}

export interface Token {
    access_token: string;
    token_type: string; // bearer
}
