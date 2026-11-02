import { StrictMode } from "react"; // StrictMode runs extra development checks to catch mistakes
import { createRoot } from "react-dom/client"; // createRoot connects React to the HTML page

import App from "./App"; // Import the top-level App component
import "./styles/index.css"; // Load the stylesheet (class slots only for now)

// Find the <div id="root"> element in index.html and render the app inside it
createRoot(document.getElementById("root")).render(
  // StrictMode wraps the app and warns about unsafe patterns
  <StrictMode>
    {/* Render the top-level App component */}
    <App />
  </StrictMode>
);
