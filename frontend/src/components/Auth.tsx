// TODO: Implement auth logic in Auth.tsx
import React, { useState } from "react";
import { api, Token } from "../api";
import { useLocation } from "react-router-dom";

interface AuthProps {
    // onAuth accepts optional returnTo path so we can navigate back after login
    onAuth: (token: Token, returnTo?: string) => void;
}

type Mode = "login" | "register";

const Auth: React.FC<AuthProps> = ({ onAuth }) => {
    const [mode, setMode] = useState<Mode>("login");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [successMsg, setSuccessMsg] = useState<string | null>(null);

    const location = useLocation();

    async function submit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setSuccessMsg(null);
        setLoading(true);
        try {
            if (mode === "login") {
                const token = await api.login(username, password);
                localStorage.setItem("authToken", token.access_token);
                // preserve returnTo from location.state if provided
                const state: any = location.state;
                const returnTo = state?.from as string | undefined;
                onAuth(token, returnTo);
            } else {
                if (!password) throw new Error("Password required");
                await api.register(username, password, email || undefined);
                setSuccessMsg("Registered. You can now login.");
                setMode("login");
            }
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="d-flex align-items-center justify-content-center vh-100 bg-light">
            <div className="card shadow-sm" style={{ minWidth: 360 }}>
                <div className="card-body">
                    <h1 className="h5 text-center mb-3">Spending Frustration</h1>
                    <div className="btn-group w-100 mb-3">
                        <button
                            className={`btn btn-sm ${mode === "login" ? "btn-primary" : "btn-outline-primary"}`}
                            onClick={() => setMode("login")}
                            disabled={loading}
                        >
                            Login
                        </button>
                        <button
                            className={`btn btn-sm ${mode === "register" ? "btn-primary" : "btn-outline-primary"}`}
                            onClick={() => setMode("register")}
                            disabled={loading}
                        >
                            Register
                        </button>
                    </div>
                    <form onSubmit={submit} className="d-flex flex-column gap-2">
                        <div>
                            <label className="form-label mb-1 small">Username</label>
                            <input
                                className="form-control form-control-sm"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                autoFocus
                            />
                        </div>
                        {mode === "register" && (
                            <div>
                                <label className="form-label mb-1 small">Email (optional)</label>
                                <input
                                    type="email"
                                    className="form-control form-control-sm"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        )}
                        <div>
                            <label className="form-label mb-1 small">Password</label>
                            <input
                                type="password"
                                className="form-control form-control-sm"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        {error && <div className="alert alert-danger py-1 small mb-0">{error}</div>}
                        {successMsg && <div className="alert alert-success py-1 small mb-0">{successMsg}</div>}
                        <button type="submit" className="btn btn-sm btn-primary mt-2" disabled={loading}>
                            {loading ? "Please wait..." : mode === "login" ? "Login" : "Register"}
                        </button>
                    </form>
                    <div className="mt-3 text-center small text-muted">
                        {mode === "login" ? "Enter your credentials" : "Create an account"}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Auth;
