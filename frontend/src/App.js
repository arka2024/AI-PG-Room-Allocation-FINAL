import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Map from "./pages/Map";
import Search from "./pages/Search";
import Compare from "./pages/Compare";
import Reviews from "./pages/Reviews";
import Chatbot from "./pages/Chatbot";
import Architecture from "./pages/Architecture";
import Profile from "./pages/Profile";
import EditProfile from "./pages/EditProfile";

function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route path="/" element={<Home />} />

        <Route path="/login" element={<Login />} />

        <Route path="/register" element={<Register />} />

        <Route path="/dashboard" element={<Dashboard />} />

        <Route path="/map" element={<Map />} />

        <Route path="/search" element={<Search />} />

        <Route path="/compare" element={<Compare />} />

        <Route path="/reviews" element={<Reviews />} />

        <Route path="/chatbot" element={<Chatbot />} />

        <Route path="/architecture" element={<Architecture />} />

        <Route path="/profile" element={<Profile />} />

        <Route path="/edit-profile" element={<EditProfile />} />

      </Routes>

    </BrowserRouter>
  );
}

export default App;