
import { Mail} from 'lucide-react';
import '../styles/app.css';
import githubIcon from '../assets/github.png';
export default function Footer() {
  return (
    <footer className="footer-section">
      <div>
          <p className="footer-credit">Made by Evan Wells</p>
          <p className="footer-note">Computer Science Student, Nipissing University,  North Bay</p>
          <p className="footer-note">© 2025 All Rights Reserved</p>
        </div>

        <div className="social-links">
          <a href="mailto:edwells522@my.nipissingu.ca?subject=Message from webpage" target="_blank" rel="noopener noreferrer">
            <Mail size={45} color="white" className = "social-link" />
          </a>
          <a href="https://github.com/ppurple12/Summer2025" target="_blank" rel="noopener noreferrer">
            <img src={githubIcon}  alt="GitHub" size={24} className = "social-link" />
          </a>
        </div>
    </footer>
  );
}