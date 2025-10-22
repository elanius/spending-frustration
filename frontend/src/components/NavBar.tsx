import React from "react";
import { NavLink } from "react-router-dom";
import pigLogo from "../assets/pig-logo.png";

interface NavBarProps {
    onLogout?: () => void;
}

const NavBar: React.FC<NavBarProps> = ({ onLogout }) => {
    const items: { key: string; label: string; to: string }[] = [
        { key: "dashboard", label: "Dashboard", to: "/dashboard" },
        { key: "transactions", label: "Transactions", to: "/transactions" },
        { key: "rules", label: "Rules", to: "/rules" },
        { key: "categories", label: "Categories", to: "/categories" },
        { key: "tags", label: "Tags", to: "/tags" },
    ];

    return (
        <aside style={{ width: 260 }} className="d-flex flex-column bg-light border-end vh-100">
            <div className="px-3 py-1 border-bottom">
                <div style={{ width: "100%" }}>
                    <img
                        src={pigLogo}
                        alt="Spending Frustration"
                        style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
                    />
                </div>
            </div>
            <nav className="flex-grow-1 px-2 py-3">
                <ul className="nav nav-pills flex-column gap-1">
                    {items.map((i) => (
                        <li key={i.key} className="nav-item">
                            <NavLink
                                to={i.to}
                                className={({ isActive }) => `nav-link text-start w-100 ${isActive ? "active" : ""}`}
                                style={{ borderRadius: 6 }}
                            >
                                {i.label}
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>
            <div className="px-3 py-3 border-top">
                {onLogout && (
                    <button className="btn btn-sm btn-outline-secondary w-100" onClick={onLogout}>
                        Logout
                    </button>
                )}
            </div>
        </aside>
    );
};

export default NavBar;
