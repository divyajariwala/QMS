import { Configuration, LogLevel } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: "35bf5d9c-5641-4a3d-8f7a-c7afc75cf538",
    authority: "https://login.microsoftonline.com/18a59a81-eea8-4c30-948a-d8824cdc2580",
    redirectUri: "/auth/callback",
    postLogoutRedirectUri: "/logout",
    navigateToLoginRequestUrl: false,

  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: true, 
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) {
          return;
        }
        switch (level) {
          case LogLevel.Error:
            console.error(message);
            break;
          case LogLevel.Info:
            console.info(message);
            break;
          case LogLevel.Verbose:
            console.debug(message);
            break;
          case LogLevel.Warning:
            console.warn(message);
            break;
        }
      },
    },
  },
};