const ENV: string = process.env.VITE_API_URL ?? "development";
 
// Base URL for your primary API
export const API_BASE_URL = (() => {
  switch (ENV) {
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