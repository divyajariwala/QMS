import "@fontsource/lato/100.css";
import "@fontsource/lato/300.css";
import "@fontsource/lato/400.css";
import "@fontsource/lato/700.css";
import "@fontsource/lato/900.css";
import { ThemeProvider } from "@mui/material/styles";
import { ErrorBoundary } from "react-error-boundary";
import { BrowserRouter, Route, Routes } from "react-router-dom";
// import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./auth/ProtectedRoute";
import { ToastContainer } from "react-toastify";
// import ProductComplaints from "./components/productComplaints/productComplaints";
import Dashboard from "./containers/dashboard/Dashboard";
import theme from "./customTheme/theme";
import Layout from "./layout/Layout";
import AuthCallback from "./auth/AuthCallback";
// import LogoutCallback from "./auth/LogoutCallback";
import "./App.scss";
// import { COMPLAINT_ID_NAME, COMPLAINT_SESSION_ID } from "./constants";
import Deviations from "@components/deviations/Deviations";
import CreateNarrative from "@components/Complaints/createNarrative";
import Complaints from "@components/complaint/Complaints";
import ComplaintsIntermediate from "@components/complaint/ComplaintsIntermediate";
import ComplaintsDetails from "@components/complaint/ComplaintsDetails";
import AdverseEvent from "@components/adverseEvent/AdverseEvent";
import { PollingProvider } from "@components/polling/PollingProvider";
import { StatusProvider } from "./context/StatusProvider";
import { useAuth } from "react-oidc-context";
import SessionCleaner from "./auth/SessionCleaner";
import AdverseEventDetails from "@components/adverseEvent/AdverseEventDetails";
import RCADetails from "@components/deviations/RCADetails";
import GradingDetails from "@components/deviations/GradingDetails";
import Spinner from "@components/common/Spinner/Spinner";
import ProcessedDeviation from "@components/deviations/ProcessedDeviations";
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

// const queryParams = new URLSearchParams(location.search);
// const cId = queryParams.get(COMPLAINT_ID_NAME) ?? "";
// const sId = queryParams.get(COMPLAINT_SESSION_ID) ?? "";

// const isAuthorized = cId || sId;

const App = () => {
  const auth = useAuth();

  if (auth.isLoading) {
    return <Spinner />;
  }

  if (auth.error) {
    return <div>Encountering error... {auth.error.message}</div>;
  }
  return (
    <BrowserRouter>
      <SessionCleaner />
      {/* <AuthProvider> */}
      <PollingProvider>
        <StatusProvider>
          <ThemeProvider theme={theme}>
            <ErrorBoundary
              FallbackComponent={ErrorFallback}
              onError={errorHandler}
            >
              <ToastContainer />
              <Routes>
                <Route path="/auth/callback" element={<AuthCallback />} />
                {/* <Route
                  path="/auth/logout/callback"
                  element={<LogoutCallback />}
                /> */}
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
                    path="/approveRca/:deviationId"
                    element={
                      <ProtectedRoute>
                        <RCADetails />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/approveGrading/:deviationId"
                    element={
                      <ProtectedRoute>
                        <GradingDetails />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/processedDeviation/:deviationId"
                    element={
                      <ProtectedRoute>
                        <ProcessedDeviation />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/adverseEvent"
                    element={
                      <ProtectedRoute>
                        <AdverseEvent />
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
                  <Route
                    path="/adverseEvent/:complaintId"
                    element={
                      <ProtectedRoute>
                        <AdverseEventDetails />
                      </ProtectedRoute>
                    }
                  />
                  {/* <Route path="/" element={isAuthorized ? <Dashboard /> : <Navigate to="/unauthorized" replace />} />
              <Route path="/unauthorized" element={<Unauthorized />} /> */}
                </Route>
              </Routes>
            </ErrorBoundary>
          </ThemeProvider>
        </StatusProvider>
      </PollingProvider>
      {/* </AuthProvider> */}
    </BrowserRouter>
  );
};

export default App;
