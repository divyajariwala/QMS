import React from "react";
import { Box, Container, Link, Typography } from "@mui/material";
import { FooterProps } from "src/types";
import styles from "./Footer.module.scss";

const Footer: React.FC<FooterProps> = ({ year = new Date().getFullYear(), className }) => (
  <Box component="footer" className={`${styles.footer} ${className || ""}`}>
    <Container maxWidth="lg">
      <Typography variant="caption" color="text.secondary" className={styles.text}>
        © {year} PwC. All rights reserved. Definition: PwC refers to the PwC network and/or
        one or more of its member firms, each of which is a separate legal entity. Please see{" "}
        <Link href="https://www.pwc.com/structure" target="_blank" rel="noreferrer">
          www.pwc.com/structure
        </Link>{" "}
        for further details.
      </Typography>
    </Container>
  </Box>
);

export default Footer;