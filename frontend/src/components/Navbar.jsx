import { Link, NavLink } from "react-router-dom";
import logo from "../assets/ClarimedLogo.png";
import "./Navbar.css";

export default function Navbar() {
  return (
    <header className="nav">
      <div className="nav-wrap">
        <Link to="/" className="brand">
          <img src={logo} alt="ClariMed" />
          <span>ClariMed</span>
        </Link>

        <nav>
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/ocr">OCR</NavLink>
          <NavLink to="/process">Summarize</NavLink>
          <NavLink to="/translate">Translate</NavLink>
          <NavLink to="/tts">TTS</NavLink>
          <NavLink to="/notes">Notes</NavLink>
        </nav>
      </div>
    </header>
  );
}