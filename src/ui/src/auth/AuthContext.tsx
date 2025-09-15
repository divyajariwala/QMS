import React, { createContext, useEffect, useMemo, useState } from "react";
import { User, UserManager, WebStorageStateStore } from "oidc-client-ts";
import { oidcConfig } from "./oidcConfig";
import { AuthContextType } from "../types";

export const authContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [manager] = useState(
    () =>
      new UserManager({
        ...oidcConfig,
        userStore: new WebStorageStateStore({ store: window.sessionStorage }),
      })
  );

  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const u = await manager.getUser();
        if (!cancelled) setUser(u);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    const onLoad = (u: User) => setUser(u);
    const onUnload = () => setUser(null);
    manager.events.addUserLoaded(onLoad);
    manager.events.addUserUnloaded(onUnload);
    return () => {
      cancelled = true;
      manager.events.removeUserLoaded(onLoad);
      manager.events.removeUserUnloaded(onUnload);
    };
  }, [manager]);

  const value = useMemo<AuthContextType>(
    () => ({
      user,
      isAuthenticated: !!user && !user.expired,
      accessToken: user?.access_token,
      isLoading,
      signIn: () => manager.signinRedirect(),
      signOut: () => manager.signoutRedirect(),
      getAccessToken: async () => {
        const u = await manager.getUser();
        if (u && !u.expired) return u.access_token;
        try {
          const newUser = await manager.signinSilent();
          return newUser?.access_token;
        } catch {
          await manager.signinRedirect();
          return undefined;
        }
      },
    }),
    [isLoading, manager, user]
  );

  return <authContext.Provider value={value}>{children}</authContext.Provider>;
}
