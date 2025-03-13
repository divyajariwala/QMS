import '@fontsource/lato/100.css';
import '@fontsource/lato/300.css';
import '@fontsource/lato/400.css';
import '@fontsource/lato/700.css';
import '@fontsource/lato/900.css';
import { ThemeProvider } from "@mui/material/styles";
import { ErrorBoundary } from "react-error-boundary";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import Dashboard from "./containers/dashboard/Dashboard";
import theme from './customTheme/theme';
import Layout from "./layout/Layout";
import "./styles/App.scss";
import {
  COMPLAINT_ID_NAME,
  COMPLAINT_SESSION_ID
} from './constants';
import Unauthorized from './components/Unauthorized';

/**
 * Shows a message in case of errors.
 *
 * @returns A react component.
 */
const ErrorFallback = () => (
  <div className="error-tip">Something went wrong!</div>
);

/**
 * Handles the error.
 */
const errorHandler = (error: Error, errorInfo: { componentStack: string; }) => {
  console.log('Logging', error, errorInfo);
};

/**
 * Renders the App general component.
 *
 * @returns A react component.
 */

const queryParams = new URLSearchParams(location.search);
const cId = queryParams.get(COMPLAINT_ID_NAME) ?? '';
const sId = queryParams.get(COMPLAINT_SESSION_ID) ?? '';

const isAuthorized = cId && sId;

const App = () => {
  return (
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <ErrorBoundary FallbackComponent={ErrorFallback} onError={errorHandler}>
          <ToastContainer />
          <Routes>
            <Route element={<Layout />}>
            <Route path="/" element={isAuthorized ? <Dashboard /> : <Navigate to="/unauthorized" replace />} />
            <Route path="/unauthorized" element={<Unauthorized />} />
            </Route>
          </Routes>
        </ErrorBoundary>
      </ThemeProvider>
    </BrowserRouter>
  );
};

export default App;
