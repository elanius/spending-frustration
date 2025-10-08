// TODO: Main app entry point
import React, { useState } from "react";
import TransactionList from "./components/TransactionList";

const App: React.FC = () => {
    const [activeView] = useState<"transactions">("transactions");
    return (
        <div className="d-flex flex-column vh-100">
            <header className="navbar navbar-dark bg-dark px-3">
                <span className="navbar-brand mb-0 h1">Spending Frustration</span>
            </header>
            <div className="d-flex flex-grow-1">
                <nav className="bg-light border-end" style={{ width: "220px" }}>
                    <ul className="nav flex-column p-2">
                        <li className="nav-item">
                            <span className="nav-link active">Transactions</span>
                        </li>
                    </ul>
                </nav>
                <main className="flex-grow-1 p-3 overflow-auto">
                    {activeView === "transactions" && <TransactionList />}
                </main>
            </div>
        </div>
    );
};

export default App;
