import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { UserManager } from "oidc-client-ts";
import { oidcConfig } from "./oidcConfig";

export default function Callback() {
  const navigate = useNavigate();

    useEffect(() => {
    (async () => {
        try {
        const mgr = new UserManager(oidcConfig);
        await mgr.clearStaleState();
        await mgr.signinRedirectCallback();
        navigate("/", { replace: true });
        } catch (e: any) {
        // surface server error_description if present
        console.error("Callback error:", e?.message, e);
        alert(`Login failed: ${e?.message ?? "Unknown error"}`);
        }
    })();
    }, [navigate]);

  return null;
}
