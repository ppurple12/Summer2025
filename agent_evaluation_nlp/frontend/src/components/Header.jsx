import { Link, useNavigate } from 'react-router-dom';
import { Settings, CircleUserRound } from 'lucide-react';
import '../styles/app.css';
import icon from '../assets/aae.png';
import Profile from './Profile';
import '../styles/profile.css';
import { useEffect } from 'react';
import { useAuth } from '../components/AuthContext';

function Header() {
  const navigate = useNavigate();
  const { userId } = useAuth();

  useEffect(() => {
    if (userId < 0) {
      navigate('/login');
    }
  }, [userId, navigate]);

  return (
    <header className="navbar">
      <div className="navbar-left">
        <div>
          <Link to="/">
            <img src={icon} alt="AAE" className="logo-icon" />
          </Link>
        </div>
        <div className="title-section">
          <h1 className="app-title">Auto Agent Evaluation</h1>
          <nav className="nav-links">
            <Link to="/agents" className="nav-link">Agents</Link>
            <Link to="/roles" className="nav-link">Roles</Link>
            <Link to="/documents" className="nav-link">Documents</Link>
            <Link to="/evaluation" className="nav-link">Evaluation</Link>
            <Link to="/assignment" className="nav-link">Assignment</Link>
          </nav>
        </div>
      </div>
      <div className="navbar-right">
        <Profile />
      </div>
    </header>
  );
}

export default Header;