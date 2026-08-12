import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// StrictMode stays ON deliberately: the engine must survive the dev
// double-mount (cancelled flag + idempotent dispose), and every headless
// shot runs against the dev server, so the double-mount is exercised in QA.
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
