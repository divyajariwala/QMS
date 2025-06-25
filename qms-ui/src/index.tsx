import ReactDOM from "react-dom/client";
import App from './App';
import './index.css';
import { createBrowserHistory } from "history";
import 'react-toastify/dist/ReactToastify.css';
import reportWebVitals from './reportWebVitals';

const history = createBrowserHistory();

const path = (/#!(\/.*)$/.exec(window.location.hash) || [])[1];
if (path) {
  history.replace(path);
}

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);
root.render(
  <App />
);

reportWebVitals();
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals