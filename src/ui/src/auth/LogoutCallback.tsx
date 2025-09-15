import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { UserManager } from "oidc-client-ts";
import { oidcConfig } from "./oidcConfig";

export default function LogoutCallback() {
  const navigate = useNavigate();
  useEffect(() => {
    (async () => {
      const mgr = new UserManager(oidcConfig);
      await mgr.signoutRedirectCallback();
      navigate("/", { replace: true });
    })();
  }, [navigate]);
  return null;
}
