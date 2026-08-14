import "./App.css";

import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home.tsx";
import Setup from "./pages/Setup.tsx";
import Login from "./pages/Login.tsx";
import Signup from "./pages/Signup.tsx";
import Company from "./pages/Company.tsx";
import Insights from "./pages/Insights.tsx";
import Profile from "./pages/Profile.tsx";
import Settings from "./pages/Settings.tsx";
import Watchlist from "./pages/Watchlist.tsx";
import WhyCompany from "./pages/WhyCompany.tsx";

const topics: string[] = [
  "Technology",
  "Healthcare",
  "Financial Services",
  "Consumer Discretionary",
  "Consumer Staples",
  "Energy",
  "Industrials",
  "Materials",
  "Utilities",
  "Real Estate",
  "Communication Services",
  "Automotive",
  "Aerospace & Defense",
  "Semiconductors",
  "Software",
  "Hardware",
  "Artificial Intelligence",
  "Cybersecurity",
  "Cloud Computing",
  "Biotechnology",
  "Pharmaceuticals",
  "Banking",
  "Insurance",
  "Investment Services",
  "Retail",
  "E-Commerce",
  "Entertainment",
  "Media",
  "Telecommunications",
  "Transportation",
  "Logistics",
  "Manufacturing",
  "Construction",
  "Mining",
  "Oil & Gas",
  "Renewable Energy",
  "Food & Beverage",
  "Travel & Hospitality",
];

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/setup" element={<Setup topics={topics} />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/watchlist" element={<Watchlist />} />
        <Route path="/company" element={<Company />} />
        <Route path="/why" element={<WhyCompany />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
