import { useContext } from "react";
import { authContext } from "./AuthContext";
import { AuthContextType } from "../types";

// Keep this as a stable named function export.
export function useAuth(): AuthContextType {
  const ctx = useContext(authContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
