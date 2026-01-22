// import React from "react";
// import { Link, useLocation } from "react-router-dom";
// import pwcLogo from "../../assets/images/pwcLogo.svg";
// import { Avatar, Badge, styled, Tab, Tabs, Tooltip } from "@mui/material";
// import { useAuth } from "react-oidc-context";

// const StyledBadge = styled(Badge)(({ theme }) => ({
//   "& .MuiBadge-badge": {
//     backgroundColor: "#437EF7",
//     border: "2px solid #1C2534",
//     width: "14px",
//     height: "14px",
//     borderRadius: "50%",
//   },
// }));

// const stringToColor = (str: string) => {
//   if (!str) return "#9e9e9e"; // fallback grey
//   let hash = 0;
//   for (let i = 0; i < str.length; i++) {
//     hash = str.charCodeAt(i) + ((hash << 5) - hash);
//   }
//   let color = "#";
//   for (let i = 0; i < 3; i++) {
//     const value = (hash >> (i * 8)) & 0xff;
//     color += `00${value.toString(16)}`.slice(-2);
//   }
//   return color;
// };

// const initialsFrom = (input?: string) => {
//   const s = (input ?? "").trim();
//   if (!s) return "U"; // default
//   const parts = s.split(/\s+/).filter(Boolean);
//   const first = parts[0]?.[0] ?? "";
//   const second = parts[1]?.[0] ?? "";
//   const initials = (first + second).toUpperCase();
//   return initials || (first || "U").toUpperCase();
// };

// const stringAvatar = (display: string) => ({
//   sx: { bgcolor: stringToColor(display) },
//   children: initialsFrom(display),
// });

// /**
//  * Renders the application header.
//  *
//  * @returns A react component.
//  */
// const Header = () => {
//   const auth = useAuth();
//   const location = useLocation();

//   const displayName = `${auth?.user?.profile?.given_name ?? ""} ${
//     auth?.user?.profile?.family_name ?? ""
//   }`.trim();

//   const navLinks = [
//     { label: "Dashboard", path: "/" },
//     { label: "Complaints", path: "/complaints" },
//     { label: "Deviations", path: "/deviations" },
//     { label: "Adverse Events", path: "/adverseEvent" },
//   ];

//   // Find the index of current tab by checking if location pathname starts with path
//   const currentTab =
//     location.pathname === "/"
//       ? 0
//       : location.pathname.startsWith("/complaints") ||
//         location.pathname.startsWith("/approveComplaints")
//       ? 1
//       : location.pathname.startsWith("/deviations") ||
//         location.pathname.startsWith("/approveRca") ||
//         location.pathname.startsWith("/approveGrading")
//       ? 2
//       : location.pathname.startsWith("/adverseEvent")
//       ? 3
//       : 0;

//   return (
//     <header className="qms-header">
//       <div className="qms-header-container">
//         <div className="qms-header-container-navbar">
//           <div className="qms-header-container-navbar-left">
//             <div className="qms-header-container-navbar-brand-logo">
//               <Link to="/">
//                 <img className="brandLogo" src={pwcLogo} alt="PwC" />
//               </Link>
//             </div>
//             <div className="qms-header-container-navbar-brand-name">
//               Quality Management Toolkit
//             </div>
//           </div>
//           <div className="qms-header-container-navbar-center">
//             <Tabs
//               value={currentTab}
//               TabIndicatorProps={{ style: { display: "none" } }}
//             >
//               {navLinks.map(({ label, path }) => (
//                 <Tab
//                   key={label}
//                   label={label}
//                   component={Link}
//                   to={path}
//                   className="qms-header-navigation-tab"
//                 />
//               ))}
//             </Tabs>
//           </div>
//           <div className="qms-header-container-navbar-right">
//             <div className="qms-header-container-navbar-right-content">
//               <Tooltip title={displayName || "User"}>
//                 <StyledBadge
//                   overlap="circular"
//                   anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
//                   variant="dot"
//                 >
//                   <Avatar
//                     alt={displayName || "User"}
//                     {...stringAvatar(displayName)}
//                   />
//                 </StyledBadge>
//               </Tooltip>
//             </div>
//           </div>
//         </div>
//       </div>
//     </header>
//   );
// };

// export default Header;

// src/components/header/Header.tsx
import React, { useState, MouseEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import pwcLogo from "../../assets/images/pwcLogo.svg";
import scnDropdownIcon from "../../assets/icons/sc-dropdown-icon.svg"
import {
  Avatar,
  Badge,
  styled,
  Tab,
  Tabs,
  Tooltip,
  Menu,
  MenuItem,
  Box,
} from "@mui/material";
import { useAuth } from "react-oidc-context";

const StyledBadge = styled(Badge)(({ theme }) => ({
  "& .MuiBadge-badge": {
    backgroundColor: "#437EF7",
    border: "2px solid #1C2534",
    width: "14px",
    height: "14px",
    borderRadius: "50%",
  },
}));

const stringToColor = (str: string) => {
  if (!str) return "#9e9e9e";
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
  if (!s) return "U";
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

const Header: React.FC = () => {
  const auth = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const displayName = `${auth?.user?.profile?.given_name ?? ""} ${auth?.user?.profile?.family_name ?? ""
    }`.trim();

  const baseNavLinks = [
    { label: "Dashboard", path: "/" },
    { label: "Complaints", path: "/complaints" },
    { label: "Deviations", path: "/deviations" },
    { label: "Adverse Events", path: "/adverseEvent" },
  ];
 
  const [scnAnchorEl, setScnAnchorEl] = useState<null | HTMLElement>(null);
  const scnMenuOpen = Boolean(scnAnchorEl);

  const handleScnTabClick = (event: MouseEvent<HTMLElement>) => { 
    setScnAnchorEl(event.currentTarget);
  };

  const handleScnClose = () => setScnAnchorEl(null);

  const handleScnNavigate = (path: string) => {
    navigate(path);
    handleScnClose();
  };

  // Determine current tab index
  const currentTab =
    location.pathname === "/"
      ? 0
      : location.pathname.startsWith("/complaints") ||
        location.pathname.startsWith("/approveComplaints")
        ? 1
        : location.pathname.startsWith("/deviations") ||
          location.pathname.startsWith("/approveRca") ||
          location.pathname.startsWith("/approveGrading")
          ? 2
          : location.pathname.startsWith("/adverseEvent")
            ? 3
            : location.pathname.startsWith("/scn")
              ? 4
              : 0;

  return (
    <header className="qms-header">
      <div className="qms-header-container">
        <div className="qms-header-container-navbar">
          <div className="qms-header-container-navbar-left">
            <div className="qms-header-container-navbar-brand-logo">
              <Link to="/">
                <img className="brandLogo" src={pwcLogo} alt="PwC" />
              </Link>
            </div>
            <div className="qms-header-container-navbar-brand-name">
              Quality Management Toolkit
            </div>
          </div>

          <div className="qms-header-container-navbar-center">
            <Tabs
              value={currentTab}
              TabIndicatorProps={{ style: { display: "none" } }}
            >
              {baseNavLinks.map(({ label, path }) => (
                <Tab
                  key={label}
                  label={label}
                  component={Link}
                  to={path}
                  className="qms-header-navigation-tab"
                />
              ))}

              {/* SCN Portal tab with dropdown */}
              <Tab
                value={4}
                className="qms-header-navigation-tab"
                label={
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <span>SCN Portal</span>
                    <span className="qms-header-navigation-tab-chevron">
                      <img
                        src={scnDropdownIcon}
                        style={{
                          transform: scnMenuOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                          transition: 'transform 0.2s ease',
                          width: '21px',
                          height: '18px'
                        }}
                      />
                    </span>
                  </Box>
                }
                onClick={handleScnTabClick}
              />
            </Tabs>

            <Menu
              anchorEl={scnAnchorEl}
              open={scnMenuOpen}
              onClose={handleScnClose}
              anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
              transformOrigin={{ vertical: "top", horizontal: "center" }}
            >
              <MenuItem onClick={() => handleScnNavigate("/scn/supplier")}>
                Supplier Portal
              </MenuItem>
              {/* Add more SCN pages here if needed */}
            </Menu>
          </div>

          <div className="qms-header-container-navbar-right">
            <div className="qms-header-container-navbar-right-content">
              <Tooltip title={displayName || "User"}>
                <StyledBadge
                  overlap="circular"
                  anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
                  variant="dot"
                >
                  <Avatar
                    alt={displayName || "User"}
                    {...stringAvatar(displayName)}
                  />
                </StyledBadge>
              </Tooltip>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;