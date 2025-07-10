import React, { useState } from 'react';
import '../styles/login.css';
import { useAuth } from '../components/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function LoginPage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [company, setCompany] = useState('');
  const [department, setDepartment] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/users/login', {
        USER_EMAIL: email,
        USER_PASSWORD: password
      });
      login(res.data.user_id);
      navigate('/');
    } catch (err) {
      alert('Login failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/users/register', {
        FIRST_NAME: firstName,
        LAST_NAME: lastName,
        USER_EMAIL: email,
        USER_PASSWORD: password,
        COMPANY_NAME: company,
        COMPANY_DEPARTMENT: department
      });
      login(res.data.user_id);
      navigate('/');
    } catch (err) {
      alert('Signup failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={isSignUp ? handleSignUp : handleLogin}>
        <h2>{isSignUp ? 'Sign Up' : 'Login'}</h2>

        {isSignUp && (
          <div className="input-row">
            <input
              type="text"
              placeholder="First Name"
              required
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
            />
            <input
              type="text"
              placeholder="Last Name"
              required
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
            />
          </div>
        )}

        <div className="input-row">
          <input
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {isSignUp && (
          <div className="input-row">
            <input
              type="text"
              placeholder="Company Name"
              required
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            />
            <input
              type="text"
              placeholder="Department"
              required
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
            />
          </div>
        )}

        <button type="submit" className="submit-button">
          {isSignUp ? 'Sign Up' : 'Login'}
        </button>

        <p>
          {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button
            type="button"
            className="link-button"
            onClick={() => setIsSignUp(!isSignUp)}
          >
            {isSignUp ? 'Login' : 'Sign Up'}
          </button>
        </p>
      </form>
    </div>
  );
}
