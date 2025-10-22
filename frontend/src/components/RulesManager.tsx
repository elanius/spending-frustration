import React, { useCallback, useEffect, useState } from "react";
import { api, TextRule, TextRuleCreateInput, TextRuleUpdateInput } from "../api";

interface EditingState {
    index?: number; // position in rules array if editing existing
    form: TextRuleCreateInput | TextRuleUpdateInput;
}

const emptyTextRule: TextRuleCreateInput = { rule: "", active: true };

const RulesManager: React.FC = () => {
    const [rules, setRules] = useState<TextRule[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [editing, setEditing] = useState<EditingState | null>(null);
    const [reapplying, setReapplying] = useState(false);

    const load = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await api.get<any[]>("/rules");
            const mapped: TextRule[] = data.map((r: any) => {
                const id = r.id || r._id;
                return { id, rule: r.rule, active: r.active !== false };
            });
            setRules(mapped);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        load();
    }, [load]);

    function startCreate() {
        setEditing({ form: { ...emptyTextRule } });
    }
    function startEdit(index: number) {
        const r = rules[index];
        setEditing({ index, form: { rule: r.rule, active: r.active } });
    }
    function cancelEdit() {
        setEditing(null);
    }
    function updateForm(partial: any) {
        setEditing((e) => (e ? { ...e, form: { ...e.form, ...partial } } : e));
    }

    async function save() {
        if (!editing) return;
        try {
            if (editing.index != null) {
                const existing = rules[editing.index];
                const update: TextRuleUpdateInput = editing.form as TextRuleUpdateInput;
                await api.put(`/rules/${existing.id}`, { active: update.active, rule: update.rule });
            } else {
                const create: TextRuleCreateInput = editing.form as TextRuleCreateInput;
                await api.post("/rules", { rule: create.rule, active: create.active });
            }
            setEditing(null);
            await load();
        } catch (e: any) {
            alert(e.message);
        }
    }

    async function remove(index: number) {
        const r = rules[index];
        if (!r.id) {
            alert("Rule has no id");
            return;
        }
        if (!confirm("Delete rule?")) return;
        try {
            await api.delete(`/rules/${r.id}`);
            await load();
        } catch (e: any) {
            alert(e.message);
        }
    }

    // Toggle active state for a rule (optimistic)
    async function toggleActive(index: number) {
        const r = rules[index];
        if (!r.id) {
            alert("Cannot change active state for rule without id");
            return;
        }
        const newActive = !r.active;
        // optimistic update
        setRules((prev) => prev.map((x, i) => (i === index ? { ...x, active: newActive } : x)));
        try {
            await api.put(`/rules/${r.id}`, { active: newActive });
        } catch (e: any) {
            alert(e.message);
            await load();
        }
    }

    // Reorder rules locally and persist order to backend
    async function move(index: number, offset: number) {
        // Reordering deprecated for per-rule storage without priority.
        // Function intentionally left blank for backward compatibility.
    }

    async function reapplyAll() {
        // Call backend endpoint directly without confirmation
        setReapplying(true);
        try {
            // New endpoint: POST /apply_all_rule
            const result = await api.post<{
                success: boolean;
                details?: string;
            }>("/actions/apply_all_rules", {});
            if (!result || !result.success) {
                // keep UX simple: notify user
                alert(result.details || "Re-apply request returned unexpected response.");
            }
        } catch (e: any) {
            alert(e.message);
        } finally {
            setReapplying(false);
        }
    }

    const form = editing?.form as TextRuleCreateInput | TextRuleUpdateInput | undefined;

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <h2 className="h5 mb-0">Rules (text)</h2>
                    <div className="small text-muted">Manage textual rules that tag and categorize transactions</div>
                </div>
                <div className="d-flex gap-2">
                    <button className="btn btn-sm btn-outline-secondary" onClick={reapplyAll} disabled={reapplying}>
                        {reapplying ? "Re-applying..." : "Re-apply all rules"}
                    </button>
                    <button className="btn btn-sm btn-primary" onClick={startCreate}>
                        New Rule
                    </button>
                </div>
            </div>
            {loading && <div>Loading...</div>}
            {error && <div className="alert alert-danger py-1 small">{error}</div>}
            <div className="table-responsive mb-3" style={{ maxHeight: "50vh" }}>
                <table className="table table-sm table-striped align-middle">
                    <thead className="table-light">
                        <tr>
                            <th>#</th>
                            <th>Active</th>
                            <th>Rule Text</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {rules.map((r, i) => (
                            <tr key={r.id || i}>
                                <td>{i + 1}</td>
                                <td>
                                    <button
                                        className={`btn btn-sm ${r.active ? "btn-success" : "btn-outline-secondary"}`}
                                        onClick={() => toggleActive(i)}
                                    >
                                        {r.active ? "Active" : "Inactive"}
                                    </button>
                                </td>
                                <td
                                    className="font-monospace small"
                                    style={{
                                        whiteSpace: "nowrap",
                                        maxWidth: "40rem",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                    }}
                                >
                                    {r.rule}
                                </td>
                                <td className="text-end">
                                    <div className="btn-group btn-group-sm">
                                        <button className="btn btn-outline-secondary" onClick={() => startEdit(i)}>
                                            Edit
                                        </button>
                                        <button
                                            className="btn btn-outline-danger"
                                            onClick={() => remove(i)}
                                            disabled={!r.id}
                                        >
                                            Del
                                        </button>
                                        {/* reorder removed */}
                                    </div>
                                </td>
                            </tr>
                        ))}
                        {!loading && rules.length === 0 && (
                            <tr>
                                <td colSpan={4} className="text-center text-muted">
                                    No rules
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
            {editing && form && (
                <div className="card mb-3">
                    <div className="card-body p-3">
                        <h6 className="card-title mb-2">{editing.index != null ? "Edit Rule" : "New Rule"}</h6>
                        {/* Name field removed - rules are textual only */}
                        <div className="mb-2">
                            <label className="form-label mb-1 small">Rule Text</label>
                            <textarea
                                className="form-control form-control-sm"
                                rows={3}
                                value={form.rule}
                                onChange={(e) => updateForm({ rule: e.target.value })}
                                placeholder="merchant contains Coffee -> @coffee #caffeinated"
                            />
                        </div>
                        <div className="form-check mb-3">
                            <input
                                className="form-check-input"
                                type="checkbox"
                                id="ruleActive"
                                checked={form.active !== false}
                                onChange={(e) => updateForm({ active: e.target.checked })}
                            />
                            <label className="form-check-label small" htmlFor="ruleActive">
                                Active
                            </label>
                        </div>
                        <div className="d-flex gap-2">
                            <button
                                className="btn btn-sm btn-success"
                                onClick={save}
                                disabled={!(form.rule && form.rule.trim())}
                            >
                                Save
                            </button>
                            <button className="btn btn-sm btn-outline-secondary" onClick={cancelEdit}>
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RulesManager;
