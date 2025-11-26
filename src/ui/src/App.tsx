import "@fontsource/lato/100.css";
import "@fontsource/lato/300.css";
import "@fontsource/lato/400.css";
import "@fontsource/lato/700.css";
import "@fontsource/lato/900.css";
import { ThemeProvider } from "@mui/material/styles";
import { ErrorBoundary } from "react-error-boundary";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./auth/ProtectedRoute";
import { ToastContainer } from "react-toastify";
import ProductComplaints from "./components/productComplaints/productComplaints";
import Dashboard from "./containers/dashboard/Dashboard";
import theme from "./customTheme/theme";
import Layout from "./layout/Layout";
import Callback from "./auth/Callback";
import LogoutCallback from "./auth/LogoutCallback";
import "./App.scss";
import { COMPLAINT_ID_NAME, COMPLAINT_SESSION_ID } from "./constants";
import Deviations from "@components/deviations/Deviations";
import CreateNarrative from "@components/Complaints/createNarrative";
import Complaints from "@components/complaint/Complaints";
import ComplaintsIntermediate from "@components/complaint/ComplaintsIntermediate";
import ComplaintsDetails from "@components/complaint/ComplaintsDetails";
import { PollingProvider } from "@components/polling/PollingProvider";
// import Unauthorized from './components/Unauthorized';

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
const errorHandler = (error: Error, errorInfo: { componentStack: string }) => {
  console.log("Logging", error, errorInfo);
};

/**
 * Renders the App general component.
 *
 * @returns A react component.
 */

const queryParams = new URLSearchParams(location.search);
const cId = queryParams.get(COMPLAINT_ID_NAME) ?? "";
const sId = queryParams.get(COMPLAINT_SESSION_ID) ?? "";

const isAuthorized = cId || sId;

const App = () => {
  return (
    <BrowserRouter>
    <PollingProvider>
      <AuthProvider>
        <ThemeProvider theme={theme}>
          <ErrorBoundary
            FallbackComponent={ErrorFallback}
            onError={errorHandler}
          >
            <ToastContainer />
            <Routes>
              <Route path="/auth/callback" element={<Callback />} />
              <Route
                path="/auth/logout/callback"
                element={<LogoutCallback />}
              />
              <Route element={<Layout />}>
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/deviations"
                  element={
                    <ProtectedRoute>
                      <Deviations />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/createNarrative"
                  element={
                    <ProtectedRoute>
                      <CreateNarrative />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/complaints"
                  element={
                    <ProtectedRoute>
                      <Complaints />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/complaints/:complaintId"
                  element={
                    <ProtectedRoute>
                      <ComplaintsIntermediate />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/approveComplaints/:complaintId"
                  element={
                    <ProtectedRoute>
                      <ComplaintsDetails />
                    </ProtectedRoute>
                  }
                />
                {/* <Route path="/" element={isAuthorized ? <Dashboard /> : <Navigate to="/unauthorized" replace />} />
              <Route path="/unauthorized" element={<Unauthorized />} /> */}
              </Route>
            </Routes>
          </ErrorBoundary>
        </ThemeProvider>
      </AuthProvider>
      </PollingProvider>
    </BrowserRouter>
  );
};

export default App;
