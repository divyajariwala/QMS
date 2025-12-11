// import { useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import { UserManager } from "oidc-client-ts";
// import { oidcConfig } from "./oidcConfig";

// export default function AuthCallback() {
//   const navigate = useNavigate();

//   useEffect(() => {
//     (async () => {
//       try {
//         const mgr = new UserManager(oidcConfig);
//         await mgr.clearStaleState();
//         await mgr.signinRedirectCallback();
//         navigate("/", { replace: true });
//       } catch (e: any) {
//         // surface server error_description if present
//         console.error("Callback error:", e?.message, e);
//         alert(`Login failed: ${e?.message ?? "Unknown error"}`);
//       }
//     })();
//   }, [navigate]);

//   return null;
// }

import { useEffect } from "react";
import { useAuth } from "react-oidc-context";
import { useNavigate } from "react-router-dom";

const AuthCallback = () => {
  const auth = useAuth();
  const navigate = useNavigate();

  // SIgn Out functionality, if needed
  //  const signOutRedirect = () => {
  //     const clientId = "2dv70q5e289p69alk1qhffkf12";
  //     const logoutUri = "http://localhost:3000/";
  //     const cognitoDomain = "https://us-east-1c3fn0dmg0.auth.us-east-1.amazoncognito.com";
  //     window.location.href = `${cognitoDomain}/logout?client_id=${clientId}&logout_uri=${encodeURIComponent(logoutUri)}`;
  //   };

  //  useEffect(() => {
  //   if (auth.isAuthenticated ) {
  //        navigate("/")
  //   }

  // }, [ auth.isAuthenticated, auth]);

  useEffect(() => {
    if (auth.isLoading) return;

    if (auth.isAuthenticated) {
      const state = (auth.user?.state ?? {}) as { returnTo?: string };
      const target = state.returnTo || "/";
      navigate(target, { replace: true });
      return;
    }

    if (auth.error) {
      console.error("Error finishing sign-in:", auth.error);
      navigate("/", { replace: true });
    }
  }, [auth.isLoading, auth.isAuthenticated, auth.user, auth.error, navigate]);

  return <div>Finishing sign-in...</div>;
};

export default AuthCallback;