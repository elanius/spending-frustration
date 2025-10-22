import React, { useCallback, useEffect, useMemo, useState } from "react";
import { api, Transaction } from "../api";

interface Filters {
    merchant: string;
    category: string;
    tags: string;
    amountMin: string;
    amountMax: string;
}

const initialFilters: Filters = { merchant: "", category: "", tags: "", amountMin: "", amountMax: "" };

const Transactions: React.FC = () => {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [filters, setFilters] = useState<Filters>(initialFilters);
    const [serverFiltering, setServerFiltering] = useState(false); // toggle for future

    const load = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            if (
                serverFiltering &&
                (filters.merchant || filters.category || filters.tags || filters.amountMin || filters.amountMax)
            ) {
                const data = await api.get<Transaction[]>("/transactions/filter", {
                    merchant_contains: filters.merchant || undefined,
                    category: filters.category || undefined,
                    tags: filters.tags || undefined,
                    amount_min: filters.amountMin || undefined,
                    amount_max: filters.amountMax || undefined,
                });
                setTransactions(data);
            } else {
                const data = await api.get<Transaction[]>("/transactions");
                setTransactions(data);
            }
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [filters, serverFiltering]);

    useEffect(() => {
        load();
    }, [load]);

    const clientFiltered = useMemo(() => {
        if (serverFiltering) return transactions;
        return transactions.filter((t) => {
            if (filters.merchant && !t.merchant.toLowerCase().includes(filters.merchant.toLowerCase())) return false;
            if (filters.category && (t.category || "").toLowerCase() !== filters.category.toLowerCase()) return false;
            if (filters.tags) {
                const required = filters.tags
                    .split(",")
                    .map((s) => s.trim().toLowerCase())
                    .filter(Boolean);
                if (required.some((tag) => !(t.tags || []).map((x) => x.toLowerCase()).includes(tag))) return false;
            }
            if (filters.amountMin && t.amount < parseFloat(filters.amountMin)) return false;
            if (filters.amountMax && t.amount > parseFloat(filters.amountMax)) return false;
            return true;
        });
    }, [transactions, filters, serverFiltering]);

    function onFilterChange(e: React.ChangeEvent<HTMLInputElement>) {
        const { name, value } = e.target;
        setFilters((prev) => ({ ...prev, [name]: value }));
    }

    return (
        <div className="d-flex flex-column h-100">
            <div className="d-flex gap-2 flex-wrap align-items-end mb-3">
                <div>
                    <label className="form-label mb-0 small">Merchant</label>
                    <input
                        name="merchant"
                        value={filters.merchant}
                        onChange={onFilterChange}
                        className="form-control form-control-sm"
                    />
                </div>
                <div>
                    <label className="form-label mb-0 small">Category</label>
                    <input
                        name="category"
                        value={filters.category}
                        onChange={onFilterChange}
                        className="form-control form-control-sm"
                    />
                </div>
                <div>
                    <label className="form-label mb-0 small">Tags (comma)</label>
                    <input
                        name="tags"
                        value={filters.tags}
                        onChange={onFilterChange}
                        className="form-control form-control-sm"
                    />
                </div>
                <div>
                    <label className="form-label mb-0 small">Min Amount</label>
                    <input
                        name="amountMin"
                        value={filters.amountMin}
                        onChange={onFilterChange}
                        className="form-control form-control-sm"
                    />
                </div>
                <div>
                    <label className="form-label mb-0 small">Max Amount</label>
                    <input
                        name="amountMax"
                        value={filters.amountMax}
                        onChange={onFilterChange}
                        className="form-control form-control-sm"
                    />
                </div>
                <div className="form-check ms-2">
                    <input
                        className="form-check-input"
                        type="checkbox"
                        id="serverFiltering"
                        checked={serverFiltering}
                        onChange={(e) => setServerFiltering(e.target.checked)}
                    />
                    <label className="form-check-label small" htmlFor="serverFiltering">
                        Server filter
                    </label>
                </div>
                <button
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => {
                        setFilters(initialFilters);
                    }}
                >
                    Clear
                </button>
                <button className="btn btn-sm btn-primary" onClick={load} disabled={loading}>
                    Reload
                </button>
            </div>
            {loading && <div>Loading...</div>}
            {error && <div className="alert alert-danger py-1 small">{error}</div>}
            <div className="table-responsive flex-grow-1" style={{ overflow: "auto", minHeight: 0 }}>
                <table className="table table-sm table-striped table-hover">
                    <thead className="table-light" style={{ position: "sticky", top: 0 }}>
                        <tr>
                            <th>Date</th>
                            <th>Merchant</th>
                            <th className="text-end">Amount</th>
                            <th>Category</th>
                            <th>Tags</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {clientFiltered.map((t) => (
                            <tr key={t.id || t._id}>
                                <td>{new Date(t.date).toLocaleDateString()}</td>
                                <td>{t.merchant}</td>
                                <td className={"text-end " + (t.amount < 0 ? "text-danger" : "text-success")}>
                                    {t.amount.toFixed(2)}
                                </td>
                                <td>{t.category || ""}</td>
                                <td>{(t.tags || []).join(", ")}</td>
                                <td>{t.notes || ""}</td>
                            </tr>
                        ))}
                        {!loading && clientFiltered.length === 0 && (
                            <tr>
                                <td colSpan={6} className="text-center text-muted">
                                    No transactions
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Transactions;
