import React from "react";
import { Link } from "react-router-dom";
import pwcLogo from "../../assets/images/pwcLogo.svg";
import { Avatar, Tooltip } from "@mui/material";
import { useAuth } from "../../auth/useAuth";


const stringToColor = (str: string) => {
  if (!str) return "#9e9e9e"; // fallback grey
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  let color = "#";
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xff;
    color += `00${value.toString(16)}`.slice(-2);
  }
  return color;
};

const initialsFrom = (input?: string) => {
  const s = (input ?? "").trim();
  if (!s) return "U"; // default
  const parts = s.split(/\s+/).filter(Boolean);
  const first = parts[0]?.[0] ?? "";
  const second = parts[1]?.[0] ?? "";
  const initials = (first + second).toUpperCase();
  return initials || (first || "U").toUpperCase();
};

const stringAvatar = (display: string) => ({
  sx: { bgcolor: stringToColor(display) },
  children: initialsFrom(display),
});

/**
 * Renders the application header.
 *
 * @returns A react component.
 */
const Header = () => {
  const { user } = useAuth();

  const displayName = `${user?.profile?.given_name ?? ""} ${user?.profile?.family_name ?? ""}`.trim();

  return (
    <header className={`qms-header`}>
      <div className="qms-header-container">
        <div className="qms-header-container-navbar">
          <div className="qms-header-container-navbar-left">
            <div className="qms-header-container-navbar-brand-logo">
              <Link to="/">
                <img className="brandLogo"
                  src={pwcLogo}
                  alt="PwC"
                />
              </Link>
            </div>
            <div className="qms-header-container-navbar-brand-name">
              Quality Management Toolkit
            </div>
          </div>
          <div className="qms-header-container-navbar-right">
            <div className="qms-header-container-navbar-right-content">
              <Tooltip title={displayName || "User"}>
                <Avatar alt={displayName || "User"}  {...stringAvatar(displayName)} />
              </Tooltip>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
