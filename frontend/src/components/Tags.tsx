import React, { useEffect, useState } from "react";
import { api } from "../api";

const Tags: React.FC = () => {
    const [items, setItems] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        (async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await api.get<string[]>("/tags");
                setItems(data || []);
            } catch (e: any) {
                setError(e?.message || "Failed to load tags");
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <h2 className="h5 mb-0">Tags</h2>
                    <div className="small text-muted">List of tags used in your transactions</div>
                </div>
            </div>
            {loading && <div>Loading...</div>}
            {error && <div className="alert alert-danger py-1 small">{error}</div>}
            <div className="table-responsive">
                <table className="table table-sm table-striped align-middle">
                    <thead className="table-light">
                        <tr>
                            <th>#</th>
                            <th>Tag</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((t, i) => (
                            <tr key={t || i}>
                                <td style={{ verticalAlign: "middle" }}>{i + 1}</td>
                                <td style={{ verticalAlign: "middle" }}>{t}</td>
                            </tr>
                        ))}
                        {!loading && items.length === 0 && (
                            <tr>
                                <td colSpan={2} className="text-center text-muted">
                                    No tags
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Tags;
