import { useEffect } from "react";
import { useAuth } from "react-oidc-context";

const SessionCleaner: React.FC = () => {
  const auth = useAuth();

  useEffect(() => {
    const onPageHide = () => {
      auth.removeUser().catch(() => {
        /* ignore */
      });
    };

    // More reliable than beforeunload; fires on tab close and bfcache
    window.addEventListener("pagehide", onPageHide);
    return () => window.removeEventListener("pagehide", onPageHide);
  }, [auth]);

  return null;
};

export default SessionCleaner;
