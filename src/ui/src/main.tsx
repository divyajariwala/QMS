import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import "./App.scss";
// import { createBrowserHistory } from "history";
import "react-toastify/dist/ReactToastify.css";
import { AuthProvider } from "react-oidc-context";
import { WebStorageStateStore, type UserManagerSettings } from "oidc-client-ts";
import { AUTHORITY_URL, CALLBACK_URL, CLIENT_ID } from "./config";

// const history = createBrowserHistory();

// const safePathRegex = /^\/[a-zA-Z0-9-_/]*$/;

// const match = /#!(\/.*)$/.exec(window.location.hash);
// const path = match ? match[1] : null;

// if (path && safePathRegex.test(path)) {
//   history.replace(path);
// } else if (path) {
//   console.warn("Blocked redirection to an unsafe path:", path);
// }

const cognitoAuthConfig: UserManagerSettings = {
  authority: AUTHORITY_URL,
  client_id: CLIENT_ID,
  redirect_uri: CALLBACK_URL,
  response_type: "code",
  scope: "email openid profile",
  userStore: new WebStorageStateStore({ store: window.sessionStorage }),
};

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
// root.render(<App />);
root.render(
  <AuthProvider {...cognitoAuthConfig}>
      <App />
  </AuthProvider>
);
