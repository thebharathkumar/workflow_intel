import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import "./index.css";
import { Layout } from "./components/Layout";
import { Analyzer } from "./pages/Analyzer";
import { Canvas } from "./pages/Canvas";
import { Governance } from "./pages/Governance";
import { Landing } from "./pages/Landing";
import { Observability } from "./pages/Observability";
import { Results } from "./pages/Results";

function withLayout(node: React.ReactNode) {
  return <Layout>{node}</Layout>;
}

const router = createBrowserRouter([
  { path: "/", element: withLayout(<Landing />) },
  { path: "/analyze", element: withLayout(<Analyzer />) },
  { path: "/results/:id", element: withLayout(<Results />) },
  { path: "/results/:id/canvas", element: withLayout(<Canvas />) },
  { path: "/results/:id/governance", element: withLayout(<Governance />) },
  { path: "/results/:id/observability", element: withLayout(<Observability />) },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
