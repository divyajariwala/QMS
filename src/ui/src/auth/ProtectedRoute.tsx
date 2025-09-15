// auth/ProtectedRoute.tsx
import React from "react";
import { useAuth } from "./useAuth";

const ProtectedRoute: React.FC<React.PropsWithChildren> = ({ children }) => {
  const { isAuthenticated, isLoading, signIn } = useAuth();

  if (isLoading) return null;

  if (!isAuthenticated) {
    void signIn();   // kicks the browser to the IdP
    return null;     // render nothing while redirecting
  }

  return <>{children}</>;
};

export default ProtectedRoute;
