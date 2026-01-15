import React from "react";
import { CircularProgress} from "@mui/material";
import styles from "./Spinner.module.scss"

const Spinner: React.FC = () => {

  return <CircularProgress size="3rem" className={styles.spinner}/>;
};

export default Spinner;
