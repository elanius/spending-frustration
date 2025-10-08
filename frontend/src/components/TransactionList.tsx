import React, { useEffect, useState } from "react";

interface Transaction {
    _id: string;
    date: string;
    amount: number;
    merchant: string;
    category?: string | null;
    tags?: string[];
    notes?: string | null;
}

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const TransactionList: React.FC = () => {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const token = localStorage.getItem("authToken");
                const res = await fetch(`${API_BASE}/transactions`, {
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                });
                if (!res.ok) {
                    throw new Error(`Failed to load (${res.status})`);
                }
                const data: Transaction[] = await res.json();
                setTransactions(data);
            } catch (e: any) {
                setError(e.message || "Unknown error");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div>Loading transactions...</div>;
    if (error) return <div className="alert alert-danger">{error}</div>;
    if (!transactions.length) return <div>No transactions found.</div>;

    return (
        <div>
            <h2 className="h5 mb-3">Transactions</h2>
            <div className="table-responsive">
                <table className="table table-sm table-striped table-hover align-middle">
                    <thead className="table-light">
                        <tr>
                            <th scope="col">Date</th>
                            <th scope="col">Merchant</th>
                            <th scope="col" className="text-end">
                                Amount
                            </th>
                            <th scope="col">Category</th>
                            <th scope="col">Tags</th>
                            <th scope="col">Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {transactions.map((tx) => (
                            <tr key={tx._id}>
                                <td>{new Date(tx.date).toLocaleDateString("sk-SK")}</td>
                                <td>{tx.merchant}</td>
                                <td className={"text-end " + (tx.amount < 0 ? "text-danger" : "text-success")}>
                                    {tx.amount.toFixed(2)}
                                </td>
                                <td>{tx.category || ""}</td>
                                <td>{tx.tags && tx.tags.length ? tx.tags.join(", ") : ""}</td>
                                <td>{tx.notes || ""}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TransactionList;
