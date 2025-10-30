import React, { useEffect, useState } from "react";
import { api } from "../api";

const Categories: React.FC = () => {
    const [items, setItems] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        (async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await api.get<string[]>("/categories");
                setItems(data || []);
            } catch (e: any) {
                setError(e?.message || "Failed to load categories");
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <h2 className="h5 mb-0">Categories</h2>
                    <div className="small text-muted">List of categories used in your transactions</div>
                </div>
            </div>
            {loading && <div>Loading...</div>}
            {error && <div className="alert alert-danger py-1 small">{error}</div>}
            <div className="table-responsive">
                <table className="table table-sm table-striped align-middle">
                    <thead className="table-light">
                        <tr>
                            <th>#</th>
                            <th>Category</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((c, i) => (
                            <tr key={c || i}>
                                <td style={{ verticalAlign: "middle" }}>{i + 1}</td>
                                <td style={{ verticalAlign: "middle" }}>{c}</td>
                            </tr>
                        ))}
                        {!loading && items.length === 0 && (
                            <tr>
                                <td colSpan={2} className="text-center text-muted">
                                    No categories
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Categories;
