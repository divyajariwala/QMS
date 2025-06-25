import React from "react";
import { Link } from "react-router-dom";
import lillyLogo from "../../assets/images/Lilly-Logo.svg";

/**
 * Renders the application header.
 *
 * @returns A react component.
 */
const Header = () => {
  return (
    <header className={`pca-header`}>
      <div className="pca-header-container">
        <div className="pca-header-container-navbar">
          <div className="pca-header-container-navbar-left">
            <div className="pca-header-continer-navbar-brand-logo">
              <Link to="/dashboard">
                <img className="brandLogo"
                  src={lillyLogo}
                  alt="PwC"
                />
              </Link>
            </div>
            <div className="pca-header-continer-navbar-brand-name">
              QMS Complaints Assessment Toolkit
            </div>
          </div>
          <div className="pca-header-container-navbar-right">
            <div className="pca-header-container-navbar-right-content">
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
