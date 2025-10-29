import React, { useCallback, useEffect, useRef, useState } from "react";
import { api, TextRule, TextRuleCreateInput, TextRuleUpdateInput } from "../api";

interface EditingState {
    index?: number;
    form: TextRuleCreateInput | TextRuleUpdateInput;
}

const emptyTextRule: TextRuleCreateInput = { rule: "", active: true };

const RulesManager: React.FC = () => {
    const [rules, setRules] = useState<TextRule[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [editing, setEditing] = useState<EditingState | null>(null);
    const [reapplying, setReapplying] = useState(false);
    const [exporting, setExporting] = useState(false);
    const [importing, setImporting] = useState(false);
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const [deletingAll, setDeletingAll] = useState(false);

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
            setError(e?.message || "Failed to save rule");
        }
    }

    async function remove(index: number) {
        const r = rules[index];
        if (!r.id) {
            setError("Rule has no id");
            return;
        }
        try {
            await api.delete(`/rules/${r.id}`);
            await load();
        } catch (e: any) {
            setError(e?.message || "Failed to delete rule");
        }
    }

    async function toggleActive(index: number) {
        const r = rules[index];
        if (!r.id) {
            setError("Cannot change active state for rule without id");
            return;
        }
        const newActive = !r.active;
        setRules((prev) => prev.map((x, i) => (i === index ? { ...x, active: newActive } : x)));
        try {
            await api.put(`/rules/${r.id}`, { active: newActive });
        } catch (e: any) {
            setError(e?.message || "Failed to update rule");
            await load();
        }
    }

    async function move(index: number, offset: number) {}

    async function reapplyAll() {
        setReapplying(true);
        try {
            const result = await api.post<{
                success: boolean;
                details?: string;
            }>("/actions/apply_all_rules", {});
            if (!result || !result.success) {
                setError(result.details || "Re-apply request returned unexpected response.");
            }
        } catch (e: any) {
            setError(e?.message || "Failed to re-apply rules");
        } finally {
            setReapplying(false);
        }
    }

    const form = editing?.form as TextRuleCreateInput | TextRuleUpdateInput | undefined;

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <h2 className="h5 mb-0">Rules</h2>
                    <div className="small text-muted">Manage textual rules that tag and categorize transactions</div>
                </div>
                <div className="d-flex gap-2">
                    <button
                        className="btn btn-sm btn-outline-secondary"
                        onClick={async () => {
                            // Export rules to a text file
                            setExporting(true);
                            try {
                                const data = await api.get<string[]>("/rules/export");
                                const text = (data || []).join("\n");
                                const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement("a");
                                a.href = url;
                                a.download = "rules.txt";
                                document.body.appendChild(a);
                                a.click();
                                a.remove();
                                URL.revokeObjectURL(url);
                            } catch (e: any) {
                                setError(e?.message || "Failed to export rules");
                            } finally {
                                setExporting(false);
                            }
                        }}
                        disabled={exporting}
                    >
                        {exporting ? "Exporting..." : "Export"}
                    </button>
                    <button
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => {
                            // trigger hidden file input
                            fileInputRef.current?.click();
                        }}
                        disabled={importing}
                    >
                        {importing ? "Importing..." : "Import"}
                    </button>
                    <button
                        className="btn btn-sm btn-outline-danger"
                        onClick={async () => {
                            // One-click: delete all rules without confirmation
                            setDeletingAll(true);
                            try {
                                // collect ids
                                const ids = rules.map((r) => r.id).filter((id): id is string => !!id);
                                for (const id of ids) {
                                    try {
                                        await api.delete(`/rules/${id}`);
                                    } catch (err) {
                                        // continue deleting remaining rules, but notify user after
                                        console.error("Failed to delete rule", id, err);
                                    }
                                }
                                await load();
                            } catch (e: any) {
                                setError(e?.message || "Failed to delete all rules");
                            } finally {
                                setDeletingAll(false);
                            }
                        }}
                        disabled={deletingAll}
                    >
                        {deletingAll ? "Deleting..." : "Delete All"}
                    </button>
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
                                    <div className="form-check form-switch">
                                        <input
                                            className="form-check-input"
                                            type="checkbox"
                                            id={`ruleSwitch${i}`}
                                            checked={r.active}
                                            onChange={() => toggleActive(i)}
                                            aria-label={r.active ? "Active" : "Inactive"}
                                        />
                                        <label className="visually-hidden" htmlFor={`ruleSwitch${i}`}>
                                            {r.active ? "Active" : "Inactive"}
                                        </label>
                                    </div>
                                </td>
                                <td
                                    className={`font-monospace small ${r.active ? "" : "text-muted"}`}
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
                        <div className="form-check form-switch mb-3">
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
            {/* Hidden file input used for importing rules as plain text (one rule per line) */}
            <input
                ref={fileInputRef}
                type="file"
                accept=".txt,text/plain"
                style={{ display: "none" }}
                onChange={async (e) => {
                    const f = e.target.files && e.target.files[0];
                    if (!f) return;
                    setImporting(true);
                    try {
                        const text = await f.text();
                        const lines = text
                            .split(/\r?\n/)
                            .map((l) => l.trim())
                            .filter((l) => l.length > 0);
                        if (lines.length === 0) {
                            setError("No rules found in the file");
                        } else {
                            await api.post("/rules/import", lines);
                            await load();
                        }
                    } catch (err: any) {
                        setError(err?.message || "Failed to import rules");
                    } finally {
                        // reset input so same file can be re-selected
                        if (fileInputRef.current) fileInputRef.current.value = "";
                        setImporting(false);
                    }
                }}
            />
        </div>
    );
};
export default RulesManager;
