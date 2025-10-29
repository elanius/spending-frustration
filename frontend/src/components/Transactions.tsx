import React, { useCallback, useEffect, useMemo, useState } from "react";
import { api, Transaction } from "../api";

interface Filters {
    dateFrom: string;
    dateTo: string;
    type: string;
    counterparty: string;
    category: string;
    tags: string;
    amountMin: string;
    amountMax: string;
}

const initialFilters: Filters = {
    dateFrom: "",
    dateTo: "",
    type: "",
    counterparty: "",
    category: "",
    tags: "",
    amountMin: "",
    amountMax: "",
};

const Transactions: React.FC = () => {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [filters, setFilters] = useState<Filters>(initialFilters);

    const load = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            // Always fetch full list for now; filtering is done client-side
            const data = await api.get<Transaction[]>("/transactions");
            setTransactions(data);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        load();
    }, [load]);

    const clientFiltered = useMemo(() => {
        return transactions.filter((t) => {
            const cp = t.counterparty;
            const counterpartyName = (
                cp?.merchant?.name ||
                cp?.bank?.account_name ||
                cp?.wallet?.wallet_name ||
                ""
            ).toLowerCase();

            // Date range filter
            try {
                const txDate = new Date(t.date);
                if (filters.dateFrom) {
                    const from = new Date(filters.dateFrom);
                    if (txDate < from) return false;
                }
                if (filters.dateTo) {
                    const to = new Date(filters.dateTo);
                    to.setHours(23, 59, 59, 999);
                    if (txDate > to) return false;
                }
            } catch (e) {
                // ignore date parse problems
            }

            // Type filter
            if (filters.type) {
                const typeVal = (t.transaction_type || t.details?.operation_type || "").toLowerCase();
                if (!typeVal.includes(filters.type.toLowerCase())) return false;
            }

            // Counterparty filter
            if (filters.counterparty && !counterpartyName.includes(filters.counterparty.toLowerCase())) return false;

            // Category filter: word-prefix match (match after first letter)
            if (filters.category) {
                const cat = (t.category || "").toLowerCase();
                const needle = filters.category.toLowerCase();
                const words = cat.split(/\s+/).filter(Boolean);
                const matched = words.some((w) => w.startsWith(needle));
                if (!matched) return false;
            }

            // Tags filter (comma separated required tags)
            if (filters.tags) {
                const required = filters.tags
                    .split(",")
                    .map((s) => s.trim().toLowerCase())
                    .filter(Boolean);
                if (required.some((tag) => !(t.tags || []).map((x) => x.toLowerCase()).includes(tag))) return false;
            }

            // Amount range
            if (filters.amountMin && t.amount < parseFloat(filters.amountMin)) return false;
            if (filters.amountMax && t.amount > parseFloat(filters.amountMax)) return false;

            return true;
        });
    }, [transactions, filters]);

    // Expanded rows tracked by id
    const [expandedIds, setExpandedIds] = useState<Record<string, boolean>>({});

    function toggleExpanded(id: string) {
        setExpandedIds((prev) => ({ ...prev, [id]: !prev[id] }));
    }

    function onFilterChange(e: React.ChangeEvent<HTMLInputElement>) {
        const { name, value } = e.target;
        setFilters((prev) => ({ ...prev, [name]: value }));
    }

    return (
        <div className="d-flex flex-column h-100">
            <div className="d-flex gap-2 flex-wrap align-items-end mb-3">
                <div>
                    <label className="form-label mb-0 small">Date from</label>
                    <input
                        type="date"
                        name="dateFrom"
                        value={filters.dateFrom}
                        onChange={onFilterChange}
                        className="form-control form-control-sm"
                    />
                </div>
                <div>
                    <label className="form-label mb-0 small">Date to</label>
                    <input
                        type="date"
                        name="dateTo"
                        value={filters.dateTo}
                        onChange={onFilterChange}
                        className="form-control form-control-sm"
                    />
                </div>
                <div>
                    <label className="form-label mb-0 small">Type</label>
                    <input
                        name="type"
                        value={filters.type}
                        onChange={onFilterChange}
                        className="form-control form-control-sm"
                    />
                </div>
                <div>
                    <label className="form-label mb-0 small">Counterparty</label>
                    <input
                        name="counterparty"
                        value={filters.counterparty}
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
                {/* server-side filtering disabled: client-side only */}
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
                            <th style={{ width: 120 }}>Date</th>
                            <th style={{ width: 150 }}>Type</th>
                            <th>Counterparty</th>
                            <th>Category</th>
                            <th>Tags</th>
                            <th className="text-end" style={{ width: 120 }}>
                                Amount
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {clientFiltered.map((t) => {
                            const key = t.id || t._id;
                            const date = (() => {
                                try {
                                    const d = new Date(t.date);
                                    const dd = String(d.getDate()).padStart(2, "0");
                                    const mm = String(d.getMonth() + 1).padStart(2, "0");
                                    const yy = d.getFullYear();
                                    return `${dd}.${mm}.${yy}`;
                                } catch (e) {
                                    return t.date;
                                }
                            })();

                            const type = t.transaction_type || t.details?.operation_type || "";
                            const counterparty =
                                t.counterparty?.merchant?.name ||
                                t.counterparty?.bank?.account_name ||
                                t.counterparty?.wallet?.wallet_name ||
                                "";
                            const tags = (t.tags || []).join(", ");
                            const notes = t.note || t.notes || t.description || "";
                            const expanded = !!expandedIds[String(key)];
                            const expandedId = `${key}-expanded`;
                            return (
                                <React.Fragment key={key}>
                                    <tr
                                        onClick={() => toggleExpanded(String(key))}
                                        style={{ cursor: "pointer" }}
                                        className={expanded ? "table-active" : undefined}
                                    >
                                        <td style={{ verticalAlign: "middle" }}>{date}</td>
                                        <td style={{ verticalAlign: "middle" }}>{type}</td>
                                        <td style={{ verticalAlign: "middle" }}>{counterparty}</td>
                                        <td style={{ verticalAlign: "middle" }}>{t.category || ""}</td>
                                        <td style={{ verticalAlign: "middle" }}>{tags}</td>
                                        <td
                                            className={"text-end " + (t.amount < 0 ? "text-danger" : "text-success")}
                                            style={{ verticalAlign: "middle" }}
                                        >
                                            {t.amount.toFixed(2)}
                                        </td>
                                    </tr>
                                    <tr key={expandedId} style={{ display: expanded ? "table-row" : "none" }}>
                                        <td colSpan={6} style={{ whiteSpace: "pre-wrap" }}>
                                            <div className="small text-muted mb-1">{notes}</div>
                                            {t.details && (
                                                <div className="small">
                                                    {t.details.operation_type && (
                                                        <div>Operation: {t.details.operation_type}</div>
                                                    )}
                                                    {t.details.currency && <div>Currency: {t.details.currency}</div>}
                                                    {t.details.balance != null && (
                                                        <div>Balance: {t.details.balance}</div>
                                                    )}
                                                    {t.details.location && <div>Location: {t.details.location}</div>}
                                                    {t.details.message_for_recipient && (
                                                        <div>Message: {t.details.message_for_recipient}</div>
                                                    )}
                                                    {t.details.symbols && (
                                                        <div>Symbols: {JSON.stringify(t.details.symbols)}</div>
                                                    )}
                                                    {t.counterparty?.bank && (
                                                        <div>
                                                            {t.counterparty.bank.iban && (
                                                                <div>IBAN: {t.counterparty.bank.iban}</div>
                                                            )}
                                                            {t.counterparty.bank.bic && (
                                                                <div>BIC: {t.counterparty.bank.bic}</div>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                </React.Fragment>
                            );
                        })}
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
