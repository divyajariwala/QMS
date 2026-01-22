import React from "react";
import { Box } from "@mui/material";
import styles from "./SCNQuickLinks.module.scss";

const SCNQuickLinks: React.FC = () => {
  const links = [
    { label: "Submission templates", href: "#" },
    { label: "Notification timelines", href: "#" },
    { label: "FAQs", href: "#" },
  ];

  return (
    <Box className={styles.quickLinksCard}>
      <h3 className={styles.title}>Quick links</h3>
      <ul className={styles.linksList}>
        {links.map((link, index) => (
          <li key={index}>
            <a href={link.href} className={styles.link}>
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </Box>
  );
};

export default SCNQuickLinks;