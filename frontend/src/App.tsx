// TODO: Main app entry point
import React, { useEffect, useState } from "react";
import NavBar from "./components/NavBar";
import Transactions from "./components/Transactions";
import RulesManager from "./components/RulesManager";
import Auth from "./components/Auth";
import Categories from "./components/Categories";
import Tags from "./components/Tags";
import { Token } from "./api";
import { Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";

const Dashboard: React.FC = () => (
    <div>
        <h2 className="h5">Dashboard</h2>
        <p className="text-muted">Overview will be provided in next iteration.</p>
    </div>
);

// Use dedicated components for categories and tags

const AppInner: React.FC<{ token: string | null; onLogout: () => void }> = ({ token, onLogout }) => {
    return (
        <div className="d-flex vh-100">
            <NavBar onLogout={onLogout} />
            <main className="flex-grow-1 p-3 overflow-auto">
                <Routes>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/transactions" element={<Transactions />} />
                    <Route path="/rules" element={<RulesManager />} />
                    <Route path="/categories" element={<Categories />} />
                    <Route path="/tags" element={<Tags />} />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </main>
        </div>
    );
};

const App: React.FC = () => {
    // Initialize token synchronously from localStorage to avoid redirect race on first render
    const [token, setToken] = useState<string | null>(() => localStorage.getItem("authToken"));
    const navigate = useNavigate();

    function handleAuth(t: Token, returnTo?: string) {
        setToken(t.access_token);
        localStorage.setItem("authToken", t.access_token);
        navigate(returnTo || "/dashboard", { replace: true });
    }

    function logout() {
        localStorage.removeItem("authToken");
        setToken(null);
        navigate("/login", { replace: true });
    }

    // A wrapper element that protects its children and redirects to /login preserving `from`
    const Protected: React.FC<{ children: React.ReactElement }> = ({ children }) => {
        const location = useLocation();
        if (!token) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
        return children;
    };

    return (
        <Routes>
            <Route path="/login" element={<Auth onAuth={handleAuth} />} />
            <Route
                path="/*"
                element={
                    <Protected>
                        <AppInner token={token} onLogout={logout} />
                    </Protected>
                }
            />
        </Routes>
    );
};

export default App;
