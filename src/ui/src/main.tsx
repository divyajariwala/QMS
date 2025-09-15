import ReactDOM from "react-dom/client";
import App from './App';
import './index.css';
import './App.scss';
import { createBrowserHistory } from "history";
import 'react-toastify/dist/ReactToastify.css';
 
const history = createBrowserHistory();
 
const safePathRegex = /^\/[a-zA-Z0-9-_/]*$/;
 
const match = /#!(\/.*)$/.exec(window.location.hash);
const path = match ? match[1] : null;
 
if (path && safePathRegex.test(path)) {
  history.replace(path);
} else if (path) {
  console.warn('Blocked redirection to an unsafe path:', path);
}
 
const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);
root.render(
  <App />
);
 