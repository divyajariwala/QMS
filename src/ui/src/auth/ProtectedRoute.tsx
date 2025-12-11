// // auth/ProtectedRoute.tsx
// import React from "react";
// import { useAuth } from "./useAuth";

// const ProtectedRoute: React.FC<React.PropsWithChildren> = ({ children }) => {
//   const { isAuthenticated, isLoading, signIn } = useAuth();

//   if (isLoading) return null;

//   if (!isAuthenticated) {
//     void signIn();   // kicks the browser to the IdP
//     return null;     // render nothing while redirecting
//   }

//   return <>{children}</>;
// };

// export default ProtectedRoute;


import React from "react";
import { useAuth } from "react-oidc-context";
import { useLocation } from "react-router-dom";
 
interface ProtectedRouteProps {
  children: React.ReactNode;
}
 
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const auth = useAuth();
  const location = useLocation();
 
  if (auth.isLoading) return <div>Loading...</div>;
  if (auth.error) return <div>Error: {auth.error.message}</div>;
 
  if (!auth.isAuthenticated) {
    const returnTo = location.pathname + location.search;
 
    auth.signinRedirect({
      state: {
        returnTo, // we'll use this in AuthCallback
      },
    });
 
    return null;
  }
 
  return <>{children}</>;
};
 
export default ProtectedRoute;