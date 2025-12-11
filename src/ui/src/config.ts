const ENV: string = process.env.VITE_API_URL ?? "development";

// Base URL for your primary API
export const API_BASE_URL = (() => {
  switch (ENV) {
    case "development":
      return "https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/";
    case "qa":
      return "https://gateway.pwc.com/"; // For QA
    case "prod":
      return "https://gateway.pwc.com/"; // For Production
    default:
      return "https://gateway.pwc.com/"; // For Development
  }
})();

// URL for the Executive Summary endpoint
export const EXECUTIVE_SUMMARY_URL = (() => {
  switch (ENV) {
    case "qa":
      return "https://gateway.pwc.com/"; // For QA
    case "prod":
      return "https://gateway.pwc.com/"; // For Production
    default:
      return "https://gateway.pwc.com/"; // For Development
  }
})();

// Export the environment key for diagnostic or conditional logic
export const ENVIRONMENT = ENV;

// Callback / redirect URL for Cognito / OIDC
export const CALLBACK_URL =
  (import.meta.env.VITE_CALLBACK_URL as string | undefined) ??
  "http://localhost:3000/auth/callback";

// Authority URL for Cognito / OIDC
export const AUTHORITY_URL =
  (import.meta.env.VITE_AUTHORITY_URL as string | undefined) ??
  "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_VNNwjblQJ";

// Authority URL for Cognito / OIDC
export const CLIENT_ID =
  (import.meta.env.VITE_CLIENT_ID as string | undefined) ??
  "bquatn1l7mrkvvhri2kbg00et";
