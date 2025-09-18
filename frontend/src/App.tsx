import React, { useState, useEffect } from 'react';
import './App.css';
import config from './config';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

interface Quiz {
  id: number;
  title: string;
  description: string;
  subject: string;
  difficulty: string;
  total_questions: number;
  time_limit: number;
  created_by: number;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{type: string, message: string} | null>(null);
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ 
    name: '', 
    email: '', 
    password: '', 
    confirmPassword: '',
    role: 'student'
  });

  const showNotification = (type: string, message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(config.API_BASE_URL + '/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setUser(data.user);
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('token', data.token);
        showNotification('success', 'Login successful!');
      } else {
        showNotification('error', data.detail || 'Login failed');
      }
    } catch (error) {
      showNotification('error', 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const register = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (registerForm.password !== registerForm.confirmPassword) {
      showNotification('error', 'Passwords do not match');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await fetch(config.API_BASE_URL + '/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: registerForm.name,
          email: registerForm.email,
          password: registerForm.password,
          role: registerForm.role
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        showNotification('success', 'Registration successful! Please login.');
        setRegisterForm({ name: '', email: '', password: '', confirmPassword: '', role: 'student' });
      } else {
        showNotification('error', data.detail || 'Registration failed');
      }
    } catch (error) {
      showNotification('error', 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    showNotification('success', 'Logged out successfully');
  };

  const fetchQuizzes = async () => {
    try {
      const response = await fetch(config.API_BASE_URL + '/api/quizzes');
      const data = await response.json();
      
      if (response.ok) {
        setQuizzes(data.quizzes || []);
      }
    } catch (error) {
      console.error('Error fetching quizzes:', error);
    }
  };

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    fetchQuizzes();
  }, []);

  if (notification) {
    return (
      <div className="notification" style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '5px',
        color: 'white',
        backgroundColor: notification.type === 'success' ? '#4CAF50' : '#f44336',
        zIndex: 1000
      }}>
        {notification.message}
      </div>
    );
  }

  if (!user) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h1>AI Quiz System</h1>
          
          <div className="auth-tabs">
            <button className="tab-button active">Login</button>
            <button className="tab-button">Register</button>
          </div>
          
          <form onSubmit={login} className="auth-form">
            <div className="form-group">
              <input
                type="email"
                placeholder="Email"
                value={loginForm.email}
                onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="password"
                placeholder="Password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
          
          <form onSubmit={register} className="auth-form">
            <div className="form-group">
              <input
                type="text"
                placeholder="Full Name"
                value={registerForm.name}
                onChange={(e) => setRegisterForm({...registerForm, name: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="email"
                placeholder="Email"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="password"
                placeholder="Password"
                value={registerForm.password}
                onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="password"
                placeholder="Confirm Password"
                value={registerForm.confirmPassword}
                onChange={(e) => setRegisterForm({...registerForm, confirmPassword: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <select
                value={registerForm.role}
                onChange={(e) => setRegisterForm({...registerForm, role: e.target.value})}
              >
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <button type="submit" className="btn btn-secondary" disabled={loading}>
              {loading ? 'Registering...' : 'Register'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Quiz System</h1>
        <div className="user-info">
          <span>Welcome, {user.name} ({user.role})</span>
          <button onClick={logout} className="btn btn-outline">Logout</button>
        </div>
      </header>
      
      <main className="app-main">
        <div className="dashboard">
          <h2>Available Quizzes</h2>
          
          {quizzes.length === 0 ? (
            <p>No quizzes available at the moment.</p>
          ) : (
            <div className="quizzes-grid">
              {quizzes.map((quiz) => (
                <div key={quiz.id} className="quiz-card">
                  <h3>{quiz.title}</h3>
                  <p>{quiz.description}</p>
                  <div className="quiz-meta">
                    <span className="subject">{quiz.subject}</span>
                    <span className="difficulty">{quiz.difficulty}</span>
                    <span className="questions">{quiz.total_questions} questions</span>
                    <span className="time-limit">{quiz.time_limit} minutes</span>
                  </div>
                  <button className="btn btn-primary">Take Quiz</button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
