// frontend/src/App.tsx
import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import config from './config';

// Google OAuth types
declare global {
  interface Window {
    google: any;
  }
}

// Helper function to safely convert API errors to strings
const formatErrorMessage = (error: any): string => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (Array.isArray(error)) {
    return error.map((err: any) => {
      if (typeof err === 'string') return err;
      if (typeof err === 'object' && err.msg) return err.msg;
      if (typeof err === 'object' && err.message) return err.message;
      return 'Invalid input';
    }).join(', ');
  }
  
  if (typeof error === 'object' && error !== null) {
    return error.msg || error.message || error.detail || 'An error occurred';
  }
  
  return 'An unknown error occurred';
};

// Define types
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'teacher' | 'student' | 'school_admin' | 'super_admin' | 'guest';
  school_id?: string;
}

interface Question {
  id?: string;
  question_text: string;
  question_type: string;
  options: string[];
  correct_answer: string;
  difficulty: string;
  points: number;
}

interface Quiz {
  id: string;
  title: string;
  description: string;
  questions: Question[];
  time_limit: number;
  is_public: boolean;
  created_by: number;
  user_id?: number;
  created_at: string;
  total_questions: number;
  total_points: number;
  creation_type?: string;
  topic?: string;
  difficulty?: string;
  attempts?: number;
  average_score?: number;
  created_by_admin?: boolean;
}

interface LoginPageProps {
  onLogin: (user: User) => void;
  onNotification: (type: 'success' | 'error', message: string) => void;
  onNavigate: (page: string) => void;
}

interface RegisterPageProps {
  onRegister: (user: User) => void;
  onNotification: (type: 'success' | 'error', message: string) => void;
  onNavigate: (page: string) => void;
}

interface HomePageProps {
  user: User | null;
}

interface QuizListPageProps {
  user: User | null;
  onTakeQuiz: (quiz: Quiz) => void;
  onNotification: (type: 'success' | 'error', message: string) => void;
}

interface CreateQuizPageProps {
  user: User | null;
  onNotification: (type: 'success' | 'error', message: string) => void;
}

interface TakeQuizPageProps {
  quiz: Quiz;
  user: User | null;
  onBack: () => void;
  onNotification: (type: 'success' | 'error', message: string) => void;
}

interface MyResultsPageProps {
  user: User;
  onNotification: (type: 'success' | 'error', message: string) => void;
}

interface AnalyticsDashboardProps {
  user: User;
  onNotification: (type: 'success' | 'error', message: string) => void;
}

interface School {
  id: string;
  name: string;
  type: string;
  address: string;
  city: string;
  state: string;
  country: string;
  phone: string;
  email: string;
  principal_name: string;
  established_year: number;
  max_students: number;
  max_teachers: number;
  created_at: string;
  is_active: boolean;
}

interface SchoolManagementProps {
  user: User | null;
  onNotification: (type: 'success' | 'error', message: string) => void;
  onUserUpdate: (user: User) => void;
}

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [appMode, setAppMode] = useState<'guest' | 'user' | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [selectedQuiz, setSelectedQuiz] = useState<Quiz | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState<{type: 'success' | 'error', message: string} | null>(null);

  // Auto-hide notifications
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Show notification
  const showNotification = useCallback((type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
  }, []);

  // Enhanced page navigation with loading states
  const navigateToPage = useCallback((page: string) => {
    setIsLoading(true);
    setTimeout(() => {
      setCurrentPage(page);
      setIsLoading(false);
    }, 300);
  }, []);

  const handleAppMode = useCallback((mode: 'guest' | 'user') => {
    setAppMode(mode);
    if (mode === 'guest') {
      // Create a guest user object
      const guestUser = {
        id: 0,
        name: 'Guest User',
        email: 'guest@example.com',
        role: 'guest' as const
      };
      setUser(guestUser);
      setCurrentPage('home');
    } else {
      setCurrentPage('login');
    }
  }, []);


  // Logout function
  const handleLogout = useCallback(async () => {
    try {
      // Call logout API if it exists (optional) - only for registered users
      if (user && user.role !== 'guest') {
        // await fetch(`${config.API_BASE_URL}/api/logout`, { method: 'POST' });
      }
      
      // Clear user state
      setUser(null);
      setAppMode(null);
      
      // Redirect to landing page
      navigateToPage('landing');
      
      // Show success notification
      showNotification('success', user?.role === 'guest' ? 'Guest session ended!' : 'Logged out successfully!');
    } catch (error) {
      // Even if API call fails, still logout locally
      setUser(null);
      setAppMode(null);
      navigateToPage('landing');
      showNotification('success', user?.role === 'guest' ? 'Guest session ended!' : 'Logged out successfully!');
    }
  }, [navigateToPage, showNotification, user]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI-Powered Quiz System Agent</h1>
        <p>Welcome to the Quiz Management System</p>
        {currentPage !== 'landing' && (
          <nav>
            <button 
              onClick={() => navigateToPage('home')}
              className={currentPage === 'home' ? 'active' : ''}
              disabled={isLoading}
            >
              🏠 Home
            </button>
            {!user && (
              <>
                <button 
                  onClick={() => navigateToPage('login')}
                  className={currentPage === 'login' ? 'active' : ''}
                  disabled={isLoading}
                >
                  🔐 Login
                </button>
                <button 
                  onClick={() => navigateToPage('register')}
                  className={currentPage === 'register' ? 'active' : ''}
                  disabled={isLoading}
                >
                  📝 Register
                </button>
              </>
            )}
            {user && (
              <>
                <button 
                  onClick={() => navigateToPage('quizzes')}
                  className={currentPage === 'quizzes' ? 'active' : ''}
                  disabled={isLoading}
                >
                  📚 Quizzes
                </button>
                <button 
                  onClick={() => navigateToPage('my-results')}
                  className={currentPage === 'my-results' ? 'active' : ''}
                  disabled={isLoading}
                >
                  📊 My Results
                </button>
                <button 
                  onClick={() => navigateToPage('create-quiz')}
                  className={currentPage === 'create-quiz' ? 'active' : ''}
                  disabled={isLoading}
                >
                  ➕ Create Quiz
                </button>
                {user && user.role === 'teacher' && (
                  <button 
                    onClick={() => navigateToPage('manage-students')}
                    className={currentPage === 'manage-students' ? 'active' : ''}
                    disabled={isLoading}
                  >
                    👥 Manage Students
                  </button>
                )}
                {user && (user.role === 'teacher' || user.role === 'admin') && (
                  <button 
                    onClick={() => navigateToPage('analytics')}
                    className={currentPage === 'analytics' ? 'active' : ''}
                    disabled={isLoading}
                  >
                    📊 Analytics
                  </button>
                )}
                {user && user.role === 'super_admin' && (
                  <button 
                    onClick={() => navigateToPage('admin-dashboard')}
                    className={currentPage === 'admin-dashboard' ? 'active' : ''}
                    disabled={isLoading}
                  >
                    👑 Super Admin Dashboard
                  </button>
                )}
              </>
            )}
            <button 
              onClick={() => navigateToPage('school-management')}
              className={currentPage === 'school-management' ? 'active' : ''}
              disabled={isLoading}
            >
              🏫 Schools
            </button>
          </nav>
        )}
        {user && (
          <div className="user-info">
            <p>Welcome, {user.name} ({user.role === 'guest' ? 'Guest Mode' : user.role})</p>
            <button onClick={handleLogout}>
              {user.role === 'guest' ? 'End Guest Session' : 'Logout'}
            </button>
          </div>
        )}
      </header>
      
      {/* Notification System */}
      {notification && (
        <div className={`notification ${notification.type}`}>
          <span>{notification.message}</span>
          <button onClick={() => setNotification(null)}>×</button>
        </div>
      )}

      {/* Loading Overlay */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      )}

      <main className={isLoading ? 'loading' : ''}>
        {currentPage === 'landing' && <LandingPage onAppMode={handleAppMode} />}
        {currentPage === 'home' && <HomePage user={user} />}
        {currentPage === 'login' && <LoginPage onLogin={setUser} onNotification={showNotification} onNavigate={navigateToPage} />}
        {currentPage === 'register' && <RegisterPage onRegister={setUser} onNotification={showNotification} onNavigate={navigateToPage} />}
        {currentPage === 'quizzes' && <QuizListPage user={user} onTakeQuiz={(quiz) => { setSelectedQuiz(quiz); navigateToPage('take-quiz'); }} onNotification={showNotification} />}
        {currentPage === 'create-quiz' && user && <CreateQuizPage user={user} onNotification={showNotification} />}
        {currentPage === 'take-quiz' && selectedQuiz && <TakeQuizPage quiz={selectedQuiz} user={user} onBack={() => navigateToPage('quizzes')} onNotification={showNotification} />}
        {currentPage === 'my-results' && user && <MyResultsPage user={user} onNotification={showNotification} />}
        {currentPage === 'analytics' && user && (user.role === 'teacher' || user.role === 'admin' || user.role === 'super_admin') && <AnalyticsDashboard user={user} onNotification={showNotification} />}
        {currentPage === 'admin-dashboard' && user && user.role === 'super_admin' && <AdminDashboard user={user} onNotification={showNotification} />}
        {currentPage === 'admin-dashboard' && user && user.role !== 'super_admin' && (
          <div className="page">
            <h2>Access Denied</h2>
            <p>Only super administrators have access to the admin dashboard.</p>
            <button onClick={() => navigateToPage('home')} className="btn">
              Return to Home
            </button>
          </div>
        )}
        {currentPage === 'school-management' && <SchoolManagement user={user} onNotification={showNotification} onUserUpdate={setUser} />}
        {currentPage === 'manage-students' && user && user.role === 'teacher' && <StudentManagement user={user} onNotification={showNotification} />}
      </main>
      
      <Footer />
    </div>
  );
}

// Home Page Component
function HomePage({ user }: HomePageProps) {
  const getRoleBasedMessage = () => {
    if (!user) return "Please login or register to access the quiz system.";
    
    switch (user.role) {
      case 'admin':
        return "Welcome, Admin! You can create quizzes, manage users, and view all system data.";
      case 'teacher':
        return "Welcome, Teacher! You can create quizzes and view student performance.";
      case 'student':
        return "Welcome, Student! You can take quizzes and view your performance.";
      default:
        return `Welcome back, ${user.name}!`;
    }
  };

  const getRoleBasedFeatures = () => {
    if (!user) {
      return (
        <div className="features">
          <div className="feature-card">
            <h3>🎯 AI Quiz Generation</h3>
            <p>Generate quizzes automatically using AI</p>
          </div>
          <div className="feature-card">
            <h3>📊 Analytics</h3>
            <p>Detailed performance insights</p>
          </div>
          <div className="feature-card">
            <h3>👥 User Management</h3>
            <p>Admin, Teacher, and Student roles</p>
          </div>
        </div>
      );
    }
    
    if (user.role === 'student') {
      return (
        <div className="features">
          <div className="feature-card">
            <h3>📚 Take Quizzes</h3>
            <p>Access and attempt available quizzes</p>
          </div>
          <div className="feature-card">
            <h3>📊 View Results</h3>
            <p>Check your quiz performance and scores</p>
          </div>
          <div className="feature-card">
            <h3>🎯 Practice Mode</h3>
            <p>Improve your knowledge with practice quizzes</p>
          </div>
        </div>
      );
    } else {
      return (
        <div className="features">
          <div className="feature-card">
            <h3>🎯 AI Quiz Generation</h3>
            <p>Generate quizzes automatically using AI</p>
          </div>
          <div className="feature-card">
            <h3>📊 Analytics</h3>
            <p>Detailed performance insights</p>
          </div>
          <div className="feature-card">
            <h3>👥 User Management</h3>
            <p>Admin, Teacher, and Student roles</p>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="page">
      <h2>Home Page</h2>
      {user ? (
        <div>
          <p>Welcome back, {user.name}!</p>
          <p><strong>Your role:</strong> {user.role.charAt(0).toUpperCase() + user.role.slice(1)}</p>
          <p className="role-message">{getRoleBasedMessage()}</p>
          {getRoleBasedFeatures()}
        </div>
      ) : (
        <div>
          <p>{getRoleBasedMessage()}</p>
          {getRoleBasedFeatures()}
        </div>
      )}
    </div>
  );
}

// Login Page Component
function LoginPage({ onLogin, onNotification, onNavigate }: LoginPageProps) {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${config.API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        onLogin(data.user);
        onNotification('success', 'Login successful! Welcome back!');
        // Redirect to home page after successful login
        setTimeout(() => {
          onNavigate('home');
        }, 1000);
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Login failed. Please check your credentials.');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className="form">
        <div className="form-row">
          <div className="form-group">
            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
            />
          </div>
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Logging in...' : '🔐 Login'}
        </button>
      </form>
    </div>
  );
}

// Register Page Component
function RegisterPage({ onRegister, onNotification, onNavigate }: RegisterPageProps) {
  const [formData, setFormData] = useState({ 
    name: '', 
    email: '', 
    password: '', 
    role: 'student' 
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${config.API_BASE_URL}/api/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        onRegister(data.user);
        onNotification('success', 'Registration successful! Welcome to the quiz system!');
        // Redirect to home page after successful registration
        setTimeout(() => {
          onNavigate('home');
        }, 1000);
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Registration failed. Please try again.');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h2>Register</h2>
      <form onSubmit={handleSubmit} className="form">
        <div className="form-row">
          <div className="form-group">
            <input
              type="text"
              placeholder="Full Name"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <input
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <select
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
            </select>
          </div>
        </div>
        <button type="submit" className="btn btn-success" disabled={loading}>
          {loading ? 'Registering...' : '📝 Register'}
        </button>
      </form>
    </div>
  );
}

// Quiz List Page Component
function QuizListPage({ user, onTakeQuiz, onNotification }: QuizListPageProps) {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const fetchQuizzes = React.useCallback(async () => {
    try {
      const url = user?.id ? `${config.API_BASE_URL}/api/quizzes?user_id=${user.id}` : `${config.API_BASE_URL}/api/quizzes`;
      const response = await fetch(url);
      const data = await response.json();
      
      if (response.ok) {
        setQuizzes(data.quizzes || []);
        if (data.quizzes && data.quizzes.length === 0) {
          onNotification('success', 'No quizzes available yet. Create your first quiz!');
        }
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Failed to fetch quizzes');
        setError(formatErrorMessage(data.detail) || 'Failed to fetch quizzes');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server');
      setError('Error connecting to server');
    } finally {
      setLoading(false);
    }
  }, [user?.id, onNotification]);

  const deleteQuiz = async (quizId: string) => {
    if (!user) return;
    
    const confirmed = window.confirm('Are you sure you want to delete this quiz? This action cannot be undone.');
    if (!confirmed) return;

    try {
      const response = await fetch(`${config.API_BASE_URL}/api/quizzes/${quizId}?user_id=${user.id}&user_role=${user.role}`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (response.ok) {
        onNotification('success', 'Quiz deleted successfully');
        // Refresh the quiz list
        fetchQuizzes();
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Failed to delete quiz');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server');
    }
  };

  const canDeleteQuiz = (quiz: Quiz) => {
    if (!user) return false;
    
    // Super admin can delete any quiz
    if (user.role === 'super_admin') return true;
    
    // Teachers and admins can only delete their own quizzes
    if (user.role === 'teacher' || user.role === 'admin') {
      return quiz.created_by === user.id || quiz.user_id === user.id;
    }
    
    return false;
  };

  React.useEffect(() => {
    fetchQuizzes();
  }, [fetchQuizzes]);

  if (loading) {
    return (
      <div className="page">
        <h2>Quizzes</h2>
        <p>Loading quizzes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <h2>Quizzes</h2>
        <p className="error">{error}</p>
      </div>
    );
  }

  return (
    <div className="page">
      <h2>Available Quizzes</h2>
      <div className="quiz-grid">
        {quizzes.map((quiz) => (
          <div key={quiz.id} className="quiz-card">
            <div className="quiz-header">
              <h3>{quiz.title}</h3>
              {canDeleteQuiz(quiz) && (
                <button 
                  className="btn btn-danger btn-small"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteQuiz(quiz.id);
                  }}
                  title="Delete Quiz"
                >
                  🗑️
                </button>
              )}
            </div>
            <p>{quiz.description}</p>
            <div className="quiz-info">
              <span>Questions: {quiz.total_questions}</span>
              <span>Points: {quiz.total_points}</span>
              <span>Time: {quiz.time_limit} min</span>
              {quiz.creation_type === 'ai_generated' && (
                <span className="ai-badge">🤖 AI Generated</span>
              )}
              {quiz.created_by_admin && (
                <span className="admin-badge">👑 Admin Created</span>
              )}
            </div>
            <button 
              className="btn btn-primary"
              onClick={() => onTakeQuiz(quiz)}
            >
              Take Quiz
            </button>
          </div>
        ))}
        {quizzes.length === 0 && (
          <p>No quizzes available. Create one to get started!</p>
        )}
      </div>
    </div>
  );
}

// Take Quiz Page Component
function TakeQuizPage({ quiz, user, onBack, onNotification }: TakeQuizPageProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [timeLeft, setTimeLeft] = useState(quiz.time_limit * 60); // Convert to seconds
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = React.useCallback(async () => {
    if (isSubmitted) return;
    
    setIsSubmitted(true);
    
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/quizzes/${quiz.id}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          quiz_id: quiz.id,
          answers: answers,
          user_id: user?.id
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setResult(data.result);
        onNotification('success', 'Quiz submitted successfully!');
      } else {
        const errorMsg = formatErrorMessage(data.detail) || 'Failed to submit quiz';
        setResult({ error: errorMsg });
        onNotification('error', errorMsg);
      }
    } catch (error) {
      const errorMsg = 'Error connecting to server';
      setResult({ error: errorMsg });
      onNotification('error', errorMsg);
    }
  }, [isSubmitted, quiz.id, answers, user?.id, onNotification]);

  React.useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [handleSubmit]);

  const handleAnswerChange = (answer: string) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answer;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };


  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isSubmitted && result) {
    return (
      <div className="page">
        <h2>Quiz Results</h2>
        {result.error ? (
          <p className="error">{result.error}</p>
        ) : (
          <div className="quiz-result">
            <div className="result-header">
              <h3>{result.quiz_title}</h3>
              <div className={`result-status ${result.passed ? 'passed' : 'failed'}`}>
                {result.status} - Grade: {result.grade_letter}
              </div>
            </div>
            
            <div className="result-summary">
              <div className="score-card">
                <h4>Your Score</h4>
                <div className="score-display">
                  <span className="score">{result.score}</span>
                  <span className="separator">/</span>
                  <span className="max-score">{result.max_score}</span>
                </div>
                <div className="percentage">{result.percentage}%</div>
              </div>
              
              <div className="grade-card">
                <h4>Grade</h4>
                <div className={`grade-display ${result.passed ? 'passed' : 'failed'}`}>
                  {result.grade_letter}
                </div>
                <div className="grade-points">({result.grade} GPA)</div>
              </div>
              
              <div className="status-card">
                <h4>Status</h4>
                <div className={`status-display ${result.passed ? 'passed' : 'failed'}`}>
                  {result.passed ? '✅ PASSED' : '❌ FAILED'}
                </div>
                <div className="pass-threshold">Passing: 60%</div>
              </div>
            </div>

            <div className="question-analysis">
              <h4>Question Analysis</h4>
              <div className="questions-list">
                {result.question_results?.map((qResult: any, index: number) => (
                  <div key={index} className={`question-result ${qResult.is_correct ? 'correct' : 'incorrect'}`}>
                    <div className="question-header">
                      <span className="question-number">Q{index + 1}</span>
                      <span className={`question-status ${qResult.is_correct ? 'correct' : 'incorrect'}`}>
                        {qResult.is_correct ? '✓' : '✗'}
                      </span>
                      <span className="question-points">
                        {qResult.points_earned}/{qResult.max_points} pts
                      </span>
                    </div>
                    <div className="question-text">{qResult.question_text}</div>
                    <div className="answer-comparison">
                      <div className="user-answer">
                        <strong>Your Answer:</strong> {qResult.user_answer}
                      </div>
                      {!qResult.is_correct && (
                        <div className="correct-answer">
                          <strong>Correct Answer:</strong> {qResult.correct_answer}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="result-actions">
              <button onClick={onBack} className="btn btn-primary">
                Back to Quizzes
              </button>
              <button onClick={() => window.location.reload()} className="btn btn-secondary">
                Take Another Quiz
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  const question = quiz.questions[currentQuestion];

  return (
    <div className="page">
      <div className="quiz-header">
        <button onClick={onBack} className="btn btn-secondary">← Back</button>
        <h2>{quiz.title}</h2>
        <div className="quiz-timer">
          Time Left: {formatTime(timeLeft)}
        </div>
      </div>
      
      <div className="quiz-progress">
        Question {currentQuestion + 1} of {quiz.questions.length}
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${((currentQuestion + 1) / quiz.questions.length) * 100}%` }}
          ></div>
        </div>
      </div>

      <div className="question-container">
        <h3>{question.question_text}</h3>
        <p>Points: {question.points} | Difficulty: {question.difficulty}</p>
        
        {question.question_type === 'multiple_choice' && (
          <div className="options-container">
            {question.options.map((option, index) => (
              <label key={index} className="option-label">
                <input
                  type="radio"
                  name="answer"
                  value={option}
                  checked={answers[currentQuestion] === option}
                  onChange={(e) => handleAnswerChange(e.target.value)}
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        )}
        
        {question.question_type === 'true_false' && (
          <div className="options-container">
            <label className="option-label">
              <input
                type="radio"
                name="answer"
                value="True"
                checked={answers[currentQuestion] === 'True'}
                onChange={(e) => handleAnswerChange(e.target.value)}
              />
              <span>True</span>
            </label>
            <label className="option-label">
              <input
                type="radio"
                name="answer"
                value="False"
                checked={answers[currentQuestion] === 'False'}
                onChange={(e) => handleAnswerChange(e.target.value)}
              />
              <span>False</span>
            </label>
          </div>
        )}
        
        {question.question_type === 'short_answer' && (
          <div className="form-group">
            <input
              type="text"
              placeholder="Your answer"
              value={answers[currentQuestion] || ''}
              onChange={(e) => handleAnswerChange(e.target.value)}
              className="answer-input"
            />
          </div>
        )}
      </div>

      <div className="quiz-navigation">
        <button 
          onClick={handlePrevious} 
          disabled={currentQuestion === 0}
          className="btn btn-secondary"
        >
          Previous
        </button>
        
        {currentQuestion === quiz.questions.length - 1 ? (
          <button 
            onClick={handleSubmit}
            className="btn btn-success"
          >
            Submit Quiz
          </button>
        ) : (
          <button 
            onClick={handleNext}
            className="btn btn-primary"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}

// Create Quiz Page Component
function CreateQuizPage({ user, onNotification }: CreateQuizPageProps) {
  const [creationMode, setCreationMode] = useState<'manual' | 'auto' | null>(null);

  return (
    <div className="page">
      <h2>Create New Quiz</h2>
      
      {!creationMode && (
        <div className="creation-mode-selector">
          <h3>Choose Quiz Creation Method</h3>
          <div className="mode-cards">
            <div className="mode-card" onClick={() => setCreationMode('manual')}>
              <div className="mode-icon">✏️</div>
              <h4>Manual Creation</h4>
              <p>Create questions manually with full control over content and format</p>
              <button className="btn btn-primary">Create Manually</button>
            </div>
            
            <div className="mode-card" onClick={() => setCreationMode('auto')}>
              <div className="mode-icon">🤖</div>
              <h4>AI Auto-Generation</h4>
              <p>Generate quiz automatically using AI based on topic and difficulty</p>
              <button className="btn btn-success">Generate with AI</button>
            </div>
          </div>
        </div>
      )}

      {creationMode === 'manual' && (
        <ManualQuizCreator 
          user={user} 
          onBack={() => setCreationMode(null)}
          onSuccess={() => setCreationMode(null)}
          onNotification={onNotification}
        />
      )}

      {creationMode === 'auto' && (
        <AutoQuizCreator 
          user={user} 
          onBack={() => setCreationMode(null)}
          onSuccess={() => setCreationMode(null)}
          onNotification={onNotification}
        />
      )}
    </div>
  );
}

// Manual Quiz Creator Component
function ManualQuizCreator({ user, onBack, onSuccess, onNotification }: { 
  user: User | null; 
  onBack: () => void; 
  onSuccess: () => void; 
  onNotification: (type: 'success' | 'error', message: string) => void;
}) {
  const [quizData, setQuizData] = useState({
    title: '',
    description: '',
    time_limit: 30,
    is_public: true
  });
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(false);

  const addQuestion = () => {
    const newQuestion: Question = {
      question_text: '',
      question_type: 'multiple_choice',
      options: ['', '', '', ''],
      correct_answer: '',
      difficulty: 'medium',
      points: 1
    };
    setQuestions([...questions, newQuestion]);
  };

  const updateQuestion = (index: number, field: keyof Question, value: any) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index] = { ...updatedQuestions[index], [field]: value };
    setQuestions(updatedQuestions);
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    if (!user) {
      onNotification('error', 'User not logged in');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${config.API_BASE_URL}/api/quizzes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...quizData,
          questions: questions,
          user_id: user.id,
          user_role: user.role
        }),
      });

      const data = await response.json();

      if (response.ok) {
        onNotification('success', 'Quiz created successfully!');
        setQuizData({ title: '', description: '', time_limit: 30, is_public: true });
        setQuestions([]);
        setTimeout(() => {
          onSuccess();
        }, 2000);
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Failed to create quiz');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="form-header">
        <button onClick={onBack} className="btn btn-secondary">← Back</button>
        <h3>Manual Quiz Creation</h3>
      </div>
      
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <input
            type="text"
            placeholder="Quiz Title"
            value={quizData.title}
            onChange={(e) => setQuizData({...quizData, title: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <textarea
            placeholder="Quiz Description"
            value={quizData.description}
            onChange={(e) => setQuizData({...quizData, description: e.target.value})}
            rows={3}
            required
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Time Limit (minutes)</label>
            <input
              type="number"
              value={quizData.time_limit}
              onChange={(e) => setQuizData({...quizData, time_limit: parseInt(e.target.value)})}
              min="1"
              required
            />
          </div>
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={quizData.is_public}
                onChange={(e) => setQuizData({...quizData, is_public: e.target.checked})}
              />
              Public Quiz
            </label>
          </div>
        </div>

        <div className="questions-section">
          <h3>Questions</h3>
          {questions.map((question, index) => (
            <div key={index} className="question-card">
              <div className="form-group">
                <input
                  type="text"
                  placeholder="Question Text"
                  value={question.question_text}
                  onChange={(e) => updateQuestion(index, 'question_text', e.target.value)}
                  required
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <select
                    value={question.question_type}
                    onChange={(e) => updateQuestion(index, 'question_type', e.target.value)}
                  >
                    <option value="multiple_choice">Multiple Choice</option>
                    <option value="true_false">True/False</option>
                    <option value="short_answer">Short Answer</option>
                  </select>
                </div>
                <div className="form-group">
                  <select
                    value={question.difficulty}
                    onChange={(e) => updateQuestion(index, 'difficulty', e.target.value)}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                <div className="form-group">
                  <input
                    type="number"
                    placeholder="Points"
                    value={question.points}
                    onChange={(e) => updateQuestion(index, 'points', parseInt(e.target.value))}
                    min="1"
                    required
                  />
                </div>
              </div>
              {question.question_type === 'multiple_choice' && (
                <div className="options-section">
                  {question.options.map((option, optIndex) => (
                    <div key={optIndex} className="form-group">
                      <input
                        type="text"
                        placeholder={`Option ${optIndex + 1}`}
                        value={option}
                        onChange={(e) => {
                          const newOptions = [...question.options];
                          newOptions[optIndex] = e.target.value;
                          updateQuestion(index, 'options', newOptions);
                        }}
                        required
                      />
                    </div>
                  ))}
                </div>
              )}
              <div className="form-group">
                <input
                  type="text"
                  placeholder="Correct Answer"
                  value={question.correct_answer}
                  onChange={(e) => updateQuestion(index, 'correct_answer', e.target.value)}
                  required
                />
              </div>
              <button
                type="button"
                onClick={() => removeQuestion(index)}
                className="btn btn-danger"
              >
                Remove Question
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addQuestion}
            className="btn btn-secondary"
          >
            Add Question
          </button>
        </div>

        <button type="submit" className="btn btn-success" disabled={loading || questions.length === 0}>
          {loading ? 'Creating Quiz...' : '📝 Create Quiz'}
        </button>
      </form>
    </div>
  );
}

// Auto Quiz Creator Component
function AutoQuizCreator({ user, onBack, onSuccess, onNotification }: {
  user: User | null;
  onBack: () => void;
  onSuccess: () => void;
  onNotification: (type: 'success' | 'error', message: string) => void;
}) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    topic: '',
    difficulty: 'medium',
    total_questions: 10,
    time_limit: 30,
    is_public: true
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    if (!user) {
      onNotification('error', 'User not logged in');
      setLoading(false);
      return;
    }

    try {
      const requestData = {
        title: formData.title,
        description: formData.description,
        subject: formData.topic,
        difficulty: formData.difficulty,
        num_questions: formData.total_questions,
        time_limit: formData.time_limit
      };

      const response = await fetch(`${config.API_BASE_URL}/api/quizzes/auto-generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...requestData,
          user_id: user.id,
          user_role: user.role
        }),
      });

      const data = await response.json();

      if (response.ok) {
        onNotification('success', 'AI-generated quiz created successfully!');
        setFormData({
          title: '',
          description: '',
          topic: '',
          difficulty: 'medium',
          total_questions: 10,
          time_limit: 30,
          is_public: true
        });
        setTimeout(() => {
          onSuccess();
        }, 2000);
      } else {
        // Handle different error types safely
        let errorMessage = 'Failed to generate quiz';
        
        if (data.detail) {
          if (typeof data.detail === 'string') {
            errorMessage = data.detail;
          } else if (Array.isArray(data.detail)) {
            errorMessage = data.detail.map((err: any) => {
              if (typeof err === 'string') return err;
              if (typeof err === 'object' && err.msg) return err.msg;
              if (typeof err === 'object' && err.message) return err.message;
              return String(err);
            }).join(', ');
          } else if (typeof data.detail === 'object') {
            errorMessage = data.detail.msg || data.detail.message || 'Unknown error occurred';
          }
        } else if (data.error) {
          if (typeof data.error === 'string') {
            errorMessage = data.error;
          } else if (typeof data.error === 'object') {
            errorMessage = data.error.message || data.error.error || 'Unknown error occurred';
          }
        } else if (data.message) {
          errorMessage = data.message;
        }
        
        onNotification('error', errorMessage);
      }
    } catch (error) {
      console.error('AI Generation Error:', error);
      onNotification('error', 'Error connecting to server. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="form-header">
        <button onClick={onBack} className="btn btn-secondary">← Back</button>
        <h3>AI Auto-Generation</h3>
      </div>
      
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <input
            type="text"
            placeholder="Quiz Title"
            value={formData.title}
            onChange={(e) => setFormData({...formData, title: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <textarea
            placeholder="Quiz Description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            rows={3}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            placeholder="Topic or Subject (e.g., 'Python Programming', 'World History', 'Mathematics')"
            value={formData.topic}
            onChange={(e) => setFormData({...formData, topic: e.target.value})}
            required
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Difficulty Level</label>
            <select
              value={formData.difficulty}
              onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div className="form-group">
            <label>Total Questions</label>
            <input
              type="number"
              value={formData.total_questions}
              onChange={(e) => setFormData({...formData, total_questions: parseInt(e.target.value)})}
              min="1"
              max="50"
              required
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Time Limit (minutes)</label>
            <input
              type="number"
              value={formData.time_limit}
              onChange={(e) => setFormData({...formData, time_limit: parseInt(e.target.value)})}
              min="1"
              required
            />
          </div>
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={formData.is_public}
                onChange={(e) => setFormData({...formData, is_public: e.target.checked})}
              />
              Public Quiz
            </label>
          </div>
        </div>

        <button type="submit" className="btn btn-success" disabled={loading}>
          {loading ? '🤖 Generating Quiz...' : '🤖 Generate Quiz with AI'}
        </button>
      </form>
    </div>
  );
}

// Footer Component
function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-section">
          <h4>Quiz Agent</h4>
          <p>AI-powered quiz creation and management platform</p>
        </div>
        
        <div className="footer-section">
          <h4>Developers</h4>
          <div className="developers">
            <p>👨‍💻 <strong>Hasnat Abdul Moiz</strong></p>
            <p>👨‍💻 <strong>Tauseef Ahmad</strong></p>
            <p className="institution">Department of Computer Science<br />Islamia College Peshawar</p>
          </div>
        </div>
        
        <div className="footer-section">
          <h4>Technologies</h4>
          <div className="tech-stack">
            <span>React</span>
            <span>FastAPI</span>
            <span>AI Models</span>
            <span>TypeScript</span>
          </div>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>&copy; 2025 Quiz Agent. All rights reserved.</p>
        <p>Built with ❤️ by Computer Science Students</p>
      </div>
    </footer>
  );
}

// My Results Page Component
function MyResultsPage({ user, onNotification }: MyResultsPageProps) {
  const [results, setResults] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResults();
  }, [user.id]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      
      // Fetch user's quiz results
      const resultsResponse = await fetch(`${config.API_BASE_URL}/api/quiz-results?user_id=${user.id}`);
      const resultsData = await resultsResponse.json();
      
      if (resultsResponse.ok) {
        setResults(resultsData.results || []);
      }
      
      // Fetch user's quiz statistics
      const statsResponse = await fetch(`${config.API_BASE_URL}/api/users/${user.id}/quiz-stats`);
      const statsData = await statsResponse.json();
      
      if (statsResponse.ok) {
        setStats(statsData);
      }
      
    } catch (error) {
      onNotification('error', 'Error loading quiz results');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="page">
        <h2>My Quiz Results</h2>
        <div className="loading">Loading your results...</div>
      </div>
    );
  }

  return (
    <div className="page">
      <h2>My Quiz Results</h2>
      
      {stats && (
        <div className="stats-overview">
          <div className="stats-grid">
            <div className="stat-card">
              <h4>Total Quizzes</h4>
              <div className="stat-value">{stats.overall_stats?.total_attempts || 0}</div>
            </div>
            <div className="stat-card">
              <h4>Average Score</h4>
              <div className="stat-value">{stats.overall_stats?.average_score || 0}%</div>
            </div>
            <div className="stat-card">
              <h4>Pass Rate</h4>
              <div className="stat-value">{stats.overall_stats?.pass_rate || 0}%</div>
            </div>
            <div className="stat-card">
              <h4>Passed</h4>
              <div className="stat-value passed">
                {stats.recent_results?.filter((r: any) => r.passed).length || 0}
              </div>
            </div>
            <div className="stat-card">
              <h4>Failed</h4>
              <div className="stat-value failed">
                {stats.recent_results?.filter((r: any) => !r.passed).length || 0}
              </div>
            </div>
          </div>
        </div>
      )}

      {results.length === 0 ? (
        <div className="no-results">
          <h3>No Quiz Results Yet</h3>
          <p>You haven't taken any quizzes yet. Start by taking a quiz from the Quizzes page!</p>
          <button onClick={() => window.location.href = '#quizzes'} className="btn btn-primary">
            Browse Quizzes
          </button>
        </div>
      ) : (
        <div className="results-list">
          <h3>Quiz History</h3>
          {results.map((result, index) => (
            <div key={result.id || index} className={`result-item ${result.passed ? 'passed' : 'failed'}`}>
              <div className="result-header">
                <h4>{result.quiz_title}</h4>
                <div className="result-meta">
                  <span className="date">{formatDate(result.submitted_at)}</span>
                  <span className={`status ${result.passed ? 'passed' : 'failed'}`}>
                    {result.status}
                  </span>
                </div>
              </div>
              
              <div className="result-details">
                <div className="score-info">
                  <span className="score">{result.score}/{result.max_score}</span>
                  <span className="percentage">{result.percentage}%</span>
                </div>
                <div className="grade-info">
                  <span className="grade">{result.grade_letter}</span>
                  <span className="gpa">({result.grade} GPA)</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Analytics Dashboard Component
function AnalyticsDashboard({ user, onNotification }: AnalyticsDashboardProps) {
  const [overview, setOverview] = useState<any>(null);
  const [students, setStudents] = useState<any[]>([]);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [selectedQuiz, setSelectedQuiz] = useState<Quiz | null>(null);
  const [quizAnalytics, setQuizAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalyticsData();
  }, [user.id]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Fetch overview analytics
      const overviewResponse = await fetch(`${config.API_BASE_URL}/api/analytics/overview?teacher_id=${user.id}`);
      const overviewData = await overviewResponse.json();
      setOverview(overviewData);
      
      // Fetch student analytics
      const studentsResponse = await fetch(`${config.API_BASE_URL}/api/analytics/students?teacher_id=${user.id}`);
      const studentsData = await studentsResponse.json();
      setStudents(studentsData.students || []);
      
      // Fetch teacher's quizzes
      const quizzesResponse = await fetch(`${config.API_BASE_URL}/api/quizzes?user_id=${user.id}`);
      const quizzesData = await quizzesResponse.json();
      setQuizzes(quizzesData.quizzes || []);
      
    } catch (error) {
      onNotification('error', 'Error loading analytics data');
    } finally {
      setLoading(false);
    }
  };

  const fetchQuizAnalytics = async (quizId: string) => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/analytics/quiz/${quizId}`);
      const data = await response.json();
      setQuizAnalytics(data);
    } catch (error) {
      onNotification('error', 'Error loading quiz analytics');
    }
  };

  const deleteQuiz = async (quizId: string) => {
    const confirmed = window.confirm('Are you sure you want to delete this quiz? This action cannot be undone.');
    if (!confirmed) return;

    try {
      const response = await fetch(`${config.API_BASE_URL}/api/quizzes/${quizId}?user_id=${user.id}&user_role=${user.role}`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (response.ok) {
        onNotification('success', 'Quiz deleted successfully');
        // Refresh the analytics data
        fetchAnalyticsData();
        // Clear selected quiz if it was deleted
        if (selectedQuiz && selectedQuiz.id === quizId) {
          setSelectedQuiz(null);
          setQuizAnalytics(null);
        }
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Failed to delete quiz');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server');
    }
  };

  const canDeleteQuiz = (quiz: Quiz) => {
    // Super admin can delete any quiz
    if (user.role === 'super_admin') return true;
    
    // Teachers and admins can only delete their own quizzes
    if (user.role === 'teacher' || user.role === 'admin') {
      return quiz.created_by === user.id || quiz.user_id === user.id;
    }
    
    return false;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="page">
        <h2>Analytics Dashboard</h2>
        <div className="loading">Loading analytics data...</div>
      </div>
    );
  }

  return (
    <div className="page">
      <h2>Analytics Dashboard</h2>
      
      <div className="analytics-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'students' ? 'active' : ''}`}
          onClick={() => setActiveTab('students')}
        >
          👥 Students
        </button>
        <button 
          className={`tab-button ${activeTab === 'quizzes' ? 'active' : ''}`}
          onClick={() => setActiveTab('quizzes')}
        >
          📚 Quizzes
        </button>
      </div>

      {activeTab === 'overview' && overview && (
        <div className="analytics-overview">
          <div className="overview-stats">
            <div className="stat-card">
              <h4>Total Quizzes</h4>
              <div className="stat-value">{overview.quizzes?.total || 0}</div>
            </div>
            <div className="stat-card">
              <h4>Total Attempts</h4>
              <div className="stat-value">{overview.performance?.total_attempts || 0}</div>
            </div>
            <div className="stat-card">
              <h4>Total Students</h4>
              <div className="stat-value">{overview.students?.total || 0}</div>
            </div>
            <div className="stat-card">
              <h4>Average Score</h4>
              <div className="stat-value">{overview.performance?.average_score || 0}%</div>
            </div>
            <div className="stat-card">
              <h4>Pass Rate</h4>
              <div className="stat-value">{overview.performance?.pass_rate || 0}%</div>
            </div>
          </div>

          {overview.performance?.total_attempts > 0 && (
            <div className="popular-quiz">
              <h3>Quiz Performance Summary</h3>
              <div className="quiz-card">
                <h4>Recent Activity</h4>
                <p>Total Attempts: {overview.performance?.total_attempts || 0}</p>
                <p>Average Score: {overview.performance?.average_score || 0}%</p>
                <p>Pass Rate: {overview.performance?.pass_rate || 0}%</p>
              </div>
            </div>
          )}

          <div className="analytics-grid">
            <div className="analytics-section">
              <h3>Grade Distribution</h3>
              <div className="grade-distribution">
                {Object.entries(overview.grade_distribution || {}).map(([grade, count]) => (
                  <div key={grade} className="grade-item">
                    <span className="grade">{grade}</span>
                    <div className="grade-bar">
                      <div 
                        className="grade-fill" 
                        style={{ width: `${(count as number / overview.total_attempts) * 100}%` }}
                      ></div>
                    </div>
                    <span className="count">{count as number}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="analytics-section">
              <h3>Subject Performance</h3>
              <div className="subject-performance">
                {Object.entries(overview.subject_performance || {}).map(([subject, data]: [string, any]) => (
                  <div key={subject} className="subject-item">
                    <h4>{subject}</h4>
                    <p>Avg Score: {data.average_score}%</p>
                    <p>Pass Rate: {data.pass_rate}%</p>
                    <p>Attempts: {data.total_attempts}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="recent-activity">
            <h3>Recent Activity</h3>
            <div className="activity-list">
              {overview.recent_activity?.map((activity: any, index: number) => (
                <div key={index} className="activity-item">
                  <div className="activity-info">
                    <h4>{activity.quiz_title}</h4>
                    <p>Score: {activity.percentage}% - Grade: {activity.grade_letter}</p>
                    <p className="activity-date">{formatDate(activity.submitted_at)}</p>
                  </div>
                  <div className={`activity-status ${activity.passed ? 'passed' : 'failed'}`}>
                    {activity.passed ? 'PASSED' : 'FAILED'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'students' && (
        <div className="students-analytics">
          <h3>Student Performance</h3>
          <div className="students-list">
            {students.map((student: any) => (
              <div key={student.id} className="student-card">
                <div className="student-info">
                  <h4>{student.name}</h4>
                  <p>{student.email}</p>
                </div>
                <div className="student-stats">
                  <div className="stat">
                    <span className="label">Quizzes:</span>
                    <span className="value">{student.performance?.total_attempts || 0}</span>
                  </div>
                  <div className="stat">
                    <span className="label">Avg Score:</span>
                    <span className="value">{student.performance?.average_score || 0}%</span>
                  </div>
                  <div className="stat">
                    <span className="label">Pass Rate:</span>
                    <span className="value">{student.performance?.pass_rate || 0}%</span>
                  </div>
                  <div className="stat">
                    <span className="label">Last Quiz:</span>
                    <span className="value">
                      {student.recent_results && student.recent_results.length > 0 
                        ? student.recent_results[0].percentage 
                        : 0}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'quizzes' && (
        <div className="quizzes-analytics">
          <h3>Quiz Analytics</h3>
          <div className="quizzes-list">
            {quizzes.map((quiz) => (
              <div key={quiz.id} className="quiz-card" onClick={() => {
                setSelectedQuiz(quiz);
                fetchQuizAnalytics(quiz.id);
              }}>
                <div className="quiz-header">
                  <h4>{quiz.title}</h4>
                  {canDeleteQuiz(quiz) && (
                    <button 
                      className="btn btn-danger btn-small"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteQuiz(quiz.id);
                      }}
                      title="Delete Quiz"
                    >
                      🗑️
                    </button>
                  )}
                </div>
                <p>Created: {formatDate(quiz.created_at)}</p>
                <p>Questions: {quiz.total_questions}</p>
                <p>Attempts: {quiz.attempts || 0}</p>
                <p>Avg Score: {quiz.average_score || 0}%</p>
                {quiz.created_by_admin && (
                  <span className="admin-badge">👑 Admin Created</span>
                )}
              </div>
            ))}
          </div>

          {selectedQuiz && quizAnalytics && (
            <div className="quiz-details">
              <h3>{selectedQuiz.title} - Detailed Analytics</h3>
              <div className="quiz-stats">
                <div className="stat">
                  <span className="label">Total Attempts:</span>
                  <span className="value">{quizAnalytics.total_attempts}</span>
                </div>
                <div className="stat">
                  <span className="label">Average Score:</span>
                  <span className="value">{quizAnalytics.average_score}%</span>
                </div>
                <div className="stat">
                  <span className="label">Pass Rate:</span>
                  <span className="value">{quizAnalytics.pass_rate}%</span>
                </div>
              </div>

              <div className="question-analysis">
                <h4>Question Analysis</h4>
                {quizAnalytics.question_analysis?.map((q: any) => (
                  <div key={q.question_number} className="question-item">
                    <div className="question-header">
                      <span>Q{q.question_number}</span>
                      <span className={`difficulty ${q.difficulty.toLowerCase()}`}>{q.difficulty}</span>
                      <span className="success-rate">{q.success_rate}%</span>
                    </div>
                    <p className="question-text">{q.question_text}</p>
                    <div className="question-stats">
                      <span>Correct: {q.correct_attempts}/{q.total_attempts}</span>
                      <span>Points: {q.points}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Admin Dashboard Component
interface AdminDashboardProps {
  user: User;
  onNotification: (type: 'success' | 'error', message: string) => void;
}

function AdminDashboard({ user, onNotification }: AdminDashboardProps) {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'teachers' | 'students' | 'credentials'>('overview');
  const [deletingUser, setDeletingUser] = useState<number | null>(null);

  useEffect(() => {
    fetchAdminDashboard();
  }, []);

  const fetchAdminDashboard = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${config.API_BASE_URL}/api/admin/dashboard?admin_id=${user.id}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch admin dashboard data');
      }
      
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching admin dashboard:', error);
      onNotification('error', 'Failed to load admin dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (userId: number, userName: string) => {
    if (!window.confirm(`Are you sure you want to delete user "${userName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setDeletingUser(userId);
      const response = await fetch(`${config.API_BASE_URL}/api/admin/users/${userId}?admin_id=${user.id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete user');
      }
      
      const result = await response.json();
      onNotification('success', result.message);
      
      // Refresh the dashboard data
      await fetchAdminDashboard();
    } catch (error) {
      console.error('Error deleting user:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      onNotification('error', `Failed to delete user: ${errorMessage}`);
    } finally {
      setDeletingUser(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="page">
        <div className="loading-spinner">Loading admin dashboard...</div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="page">
        <h2>Error</h2>
        <p>Failed to load admin dashboard data.</p>
        <button onClick={fetchAdminDashboard} className="btn">Retry</button>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>👑 Admin Dashboard</h1>
        <p>Manage all users and monitor system activity</p>
      </div>

      {/* Overview Stats */}
      <div className="overview-stats">
        <div className="stat-card">
          <h4>Total Users</h4>
          <div className="stat-value">{dashboardData?.overview?.total_users || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Teachers</h4>
          <div className="stat-value">{dashboardData?.overview?.total_teachers || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Students</h4>
          <div className="stat-value">{dashboardData?.overview?.total_students || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Total Quizzes</h4>
          <div className="stat-value">{dashboardData?.overview?.total_quizzes || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Total Attempts</h4>
          <div className="stat-value">{dashboardData?.overview?.total_attempts || 0}</div>
        </div>
        <div className="stat-card">
          <h4>Avg Score</h4>
          <div className="stat-value">{dashboardData?.overview?.average_score || 0}%</div>
        </div>
        <div className="stat-card">
          <h4>Pass Rate</h4>
          <div className="stat-value">{dashboardData?.overview?.pass_rate || 0}%</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👥 All Users
        </button>
        <button 
          className={`tab-button ${activeTab === 'teachers' ? 'active' : ''}`}
          onClick={() => setActiveTab('teachers')}
        >
          👨‍🏫 Teachers
        </button>
        <button 
          className={`tab-button ${activeTab === 'students' ? 'active' : ''}`}
          onClick={() => setActiveTab('students')}
        >
          👨‍🎓 Students
        </button>
        <button 
          className={`tab-button ${activeTab === 'credentials' ? 'active' : ''}`}
          onClick={() => setActiveTab('credentials')}
        >
          🔑 All Credentials
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="admin-content">
          <div className="analytics-grid">
            <div className="analytics-section">
              <h3>Recent Users</h3>
              <div className="activity-list">
                {(dashboardData?.recent_users || []).map((user: any, index: number) => (
                  <div key={index} className="activity-item">
                    <div className="activity-info">
                      <p><strong>{user.name}</strong> ({user.role})</p>
                      <p>Email: {user.email}</p>
                      <p className="activity-time">Registered: {formatDate(user.created_at)}</p>
                    </div>
                  </div>
                ))}
                {(!dashboardData?.recent_users || dashboardData.recent_users.length === 0) && (
                  <p>No recent users</p>
                )}
              </div>
            </div>
            
            <div className="analytics-section">
              <h3>Recent Quizzes</h3>
              <div className="activity-list">
                {(dashboardData?.recent_quizzes || []).map((quiz: any, index: number) => (
                  <div key={index} className="activity-item">
                    <div className="activity-info">
                      <p><strong>{quiz.title}</strong></p>
                      <p>Questions: {quiz.total_questions} | Points: {quiz.total_points}</p>
                      <p className="activity-time">Created: {formatDate(quiz.created_at)}</p>
                    </div>
                  </div>
                ))}
                {(!dashboardData?.recent_quizzes || dashboardData.recent_quizzes.length === 0) && (
                  <p>No recent quizzes</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="admin-content">
          <div className="users-grid">
            {(dashboardData?.users || []).map((userData: any) => (
              <div key={userData.id} className="user-card">
                <div className="user-header">
                  <h4>{userData.name}</h4>
                  <div className="user-actions">
                    <span className={`role-badge role-${userData.role}`}>
                      {userData.role.toUpperCase()}
                    </span>
                    {userData.id !== user.id && (
                      <button
                        className="delete-btn"
                        onClick={() => deleteUser(userData.id, userData.name)}
                        disabled={deletingUser === userData.id}
                        title="Delete User"
                      >
                        {deletingUser === userData.id ? '⏳' : '🗑️'}
                      </button>
                    )}
                  </div>
                </div>
                <div className="user-details">
                  <p><strong>Email:</strong> {userData.email}</p>
                  <p><strong>Password:</strong> {userData.password}</p>
                  <p><strong>ID:</strong> {userData.id}</p>
                  <p><strong>Registered:</strong> {formatDate(userData.created_at)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'teachers' && (
        <div className="admin-content">
          <div className="section-header">
            <h3>👨‍🏫 Enrolled Teachers ({dashboardData?.teachers?.length || 0})</h3>
            <p>Manage all teacher accounts in the system</p>
          </div>
          <div className="users-grid">
            {(dashboardData?.teachers || []).map((teacher: any) => (
              <div key={teacher.id} className="user-card">
                <div className="user-header">
                  <h4>{teacher.name}</h4>
                  <div className="user-actions">
                    <span className="role-badge role-teacher">TEACHER</span>
                    {teacher.id !== user.id && (
                      <button
                        className="delete-btn"
                        onClick={() => deleteUser(teacher.id, teacher.name)}
                        disabled={deletingUser === teacher.id}
                        title="Delete Teacher"
                      >
                        {deletingUser === teacher.id ? '⏳' : '🗑️'}
                      </button>
                    )}
                  </div>
                </div>
                <div className="user-details">
                  <p><strong>Email:</strong> {teacher.email}</p>
                  <p><strong>Password:</strong> {teacher.password}</p>
                  <p><strong>ID:</strong> {teacher.id}</p>
                  <p><strong>Registered:</strong> {formatDate(teacher.created_at)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'students' && (
        <div className="admin-content">
          <div className="section-header">
            <h3>👨‍🎓 Enrolled Students ({dashboardData?.students?.length || 0})</h3>
            <p>Manage all student accounts in the system</p>
          </div>
          <div className="users-grid">
            {(dashboardData?.students || []).map((student: any) => (
              <div key={student.id} className="user-card">
                <div className="user-header">
                  <h4>{student.name}</h4>
                  <div className="user-actions">
                    <span className="role-badge role-student">STUDENT</span>
                    {student.id !== user.id && (
                      <button
                        className="delete-btn"
                        onClick={() => deleteUser(student.id, student.name)}
                        disabled={deletingUser === student.id}
                        title="Delete Student"
                      >
                        {deletingUser === student.id ? '⏳' : '🗑️'}
                      </button>
                    )}
                  </div>
                </div>
                <div className="user-details">
                  <p><strong>Email:</strong> {student.email}</p>
                  <p><strong>Password:</strong> {student.password}</p>
                  <p><strong>ID:</strong> {student.id}</p>
                  <p><strong>Registered:</strong> {formatDate(student.created_at)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'credentials' && (
        <CredentialsTab user={user} onNotification={onNotification} />
      )}
    </div>
  );
}

// Credentials Tab Component
function CredentialsTab({ user, onNotification }: {
  user: User;
  onNotification: (type: 'success' | 'error', message: string) => void;
}) {
  const [credentials, setCredentials] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCredentials = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/super-admin/all-credentials?admin_id=${user.id}`);
      const data = await response.json();
      
      if (response.ok) {
        setCredentials(data.users || []);
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Failed to fetch credentials');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchCredentials();
  }, []);

  if (loading) {
    return (
      <div className="admin-content">
        <div className="loading">Loading credentials...</div>
      </div>
    );
  }

  return (
    <div className="admin-content">
      <div className="section-header">
        <h3>🔑 All User Credentials ({credentials.length})</h3>
        <p>View all user login credentials in the system</p>
        <button className="btn btn-secondary" onClick={fetchCredentials}>
          🔄 Refresh
        </button>
      </div>
      
      <div className="credentials-grid">
        {credentials.map((credential) => (
          <div key={credential.id} className="credential-card">
            <div className="credential-header">
              <h4>{credential.name}</h4>
              <span className={`role-badge role-${credential.role}`}>
                {credential.role.toUpperCase()}
              </span>
            </div>
            <div className="credential-details">
              <div className="credential-row">
                <strong>Email:</strong> {credential.email}
              </div>
              <div className="credential-row">
                <strong>Password:</strong> {credential.password}
              </div>
              <div className="credential-row">
                <strong>School ID:</strong> {credential.school_id || 'N/A'}
              </div>
              <div className="credential-row">
                <strong>Created:</strong> {new Date(credential.created_at).toLocaleDateString()}
              </div>
              {credential.created_by_teacher && (
                <div className="credential-row">
                  <strong>Created by Teacher ID:</strong> {credential.created_by_teacher}
                </div>
              )}
            </div>
            <div className="credential-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  navigator.clipboard.writeText(`Email: ${credential.email}\nPassword: ${credential.password}`);
                  onNotification('success', 'Credentials copied to clipboard!');
                }}
              >
                📋 Copy Credentials
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// School Management Component
function SchoolManagement({ user, onNotification, onUserUpdate }: SchoolManagementProps) {
  const [schools, setSchools] = useState<School[]>([]);
  const [selectedSchool, setSelectedSchool] = useState<School | null>(null);
  const [schoolQuizzes, setSchoolQuizzes] = useState<Quiz[]>([]);
  const [schoolAnalytics, setSchoolAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'schools' | 'register' | 'analytics'>('schools');
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [showRegistrationDialog, setShowRegistrationDialog] = useState(false);
  const [registrationData, setRegistrationData] = useState<any>(null);

  useEffect(() => {
    fetchSchools();
  }, []);

  const showSchoolRegistrationDialog = (data: any) => {
    setRegistrationData(data);
    setShowRegistrationDialog(true);
    
    // Auto-hide dialog after 5 seconds
    setTimeout(() => {
      setShowRegistrationDialog(false);
      // Auto-refresh page after dialog closes
      setTimeout(() => {
        window.location.reload();
      }, 500);
    }, 5000);
  };

  const fetchSchools = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${config.API_BASE_URL}/api/schools');
      const data = await response.json();
      
      if (response.ok) {
        let schoolsData = data.schools || [];
        
        // Filter schools based on user role
        if (user && user.role === 'teacher' && user.school_id) {
          // Teachers only see their own school
          schoolsData = schoolsData.filter((school: any) => school.id === user.school_id);
        } else if (user && user.role === 'student' && user.school_id) {
          // Students only see their own school
          schoolsData = schoolsData.filter((school: any) => school.id === user.school_id);
        }
        // Super admin and guests see all schools
        
        setSchools(schoolsData);
      } else {
        onNotification('error', 'Failed to fetch schools');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  const fetchSchoolQuizzes = async (schoolId: string) => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/schools/${schoolId}/quizzes`);
      const data = await response.json();
      
      if (response.ok) {
        setSchoolQuizzes(data.quizzes || []);
      } else {
        onNotification('error', 'Failed to fetch school quizzes');
      }
    } catch (error) {
      onNotification('error', 'Error fetching school quizzes');
    }
  };

  const fetchSchoolAnalytics = async (schoolId: string) => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/schools/${schoolId}/analytics`);
      const data = await response.json();
      
      if (response.ok) {
        setSchoolAnalytics(data.analytics);
      } else {
        onNotification('error', 'Failed to fetch school analytics');
      }
    } catch (error) {
      onNotification('error', 'Error fetching school analytics');
    }
  };

  const handleSchoolSelect = (school: School) => {
    setSelectedSchool(school);
    fetchSchoolQuizzes(school.id);
    fetchSchoolAnalytics(school.id);
  };

  if (loading) {
    return (
      <div className="page">
        <h2>🏫 School Management</h2>
        <div className="loading">Loading schools...</div>
      </div>
    );
  }

  return (
    <div className="page">
      <h2>🏫 School Management System</h2>
      <p>Multi-tenant school platform with isolated quiz management</p>
      {!user && (
        <div className="info-banner">
          <p>👋 Welcome! You can browse schools without logging in, but you'll need to <strong>register or login</strong> to create schools or access school-specific features.</p>
        </div>
      )}
      
      <div className="school-tabs">
        <button 
          className={`tab-button ${activeTab === 'schools' ? 'active' : ''}`}
          onClick={() => setActiveTab('schools')}
        >
          📚 All Schools
        </button>
        <button 
          className={`tab-button ${activeTab === 'register' ? 'active' : ''}`}
          onClick={() => setActiveTab('register')}
        >
          ➕ Register School
        </button>
        <button 
          className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          📊 School Analytics
        </button>
      </div>

      {activeTab === 'schools' && (
        <div className="schools-section">
          <h3>🏫 Registered Schools ({schools.length})</h3>
          <div className="schools-grid">
            {schools.map((school) => (
              <div key={school.id} className="school-card" onClick={() => handleSchoolSelect(school)}>
                <div className="school-header">
                  <h4>{school.name}</h4>
                  <span className="school-type">{school.type.toUpperCase()}</span>
                </div>
                <div className="school-details">
                  <p><strong>📍 Location:</strong> {school.city}, {school.state}, {school.country}</p>
                  <p><strong>👨‍💼 Principal:</strong> {school.principal_name}</p>
                  <p><strong>📞 Phone:</strong> {school.phone}</p>
                  <p><strong>📧 Email:</strong> {school.email}</p>
                  <p><strong>📅 Established:</strong> {school.established_year}</p>
                  <p><strong>👥 Capacity:</strong> {school.max_students} students, {school.max_teachers} teachers</p>
                </div>
                <div className="school-actions">
                  <button className="btn btn-primary">View Details</button>
                </div>
              </div>
            ))}
          </div>

          {selectedSchool && (
            <div className="school-details-section">
              <h3>🏫 {selectedSchool.name} - Details</h3>
              <div className="school-info-grid">
                <div className="school-info-card">
                  <h4>📚 School Quizzes ({schoolQuizzes.length})</h4>
                  {schoolQuizzes.length > 0 ? (
                    <div className="quizzes-list">
                      {schoolQuizzes.map((quiz) => (
                        <div key={quiz.id} className="quiz-item">
                          <h5>{quiz.title}</h5>
                          <p>Questions: {quiz.total_questions} | Points: {quiz.total_points}</p>
                          <p>Created: {new Date(quiz.created_at).toLocaleDateString()}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>No quizzes created for this school yet.</p>
                  )}
                </div>

                {schoolAnalytics && (
                  <div className="school-info-card">
                    <h4>📊 School Analytics</h4>
                    <div className="analytics-stats">
                      <div className="stat">
                        <span className="label">Students:</span>
                        <span className="value">{schoolAnalytics.total_students}</span>
                      </div>
                      <div className="stat">
                        <span className="label">Teachers:</span>
                        <span className="value">{schoolAnalytics.total_teachers}</span>
                      </div>
                      <div className="stat">
                        <span className="label">Quizzes:</span>
                        <span className="value">{schoolAnalytics.total_quizzes}</span>
                      </div>
                      <div className="stat">
                        <span className="label">Quiz Attempts:</span>
                        <span className="value">{schoolAnalytics.total_quiz_attempts}</span>
                      </div>
                      <div className="stat">
                        <span className="label">Avg Score:</span>
                        <span className="value">{schoolAnalytics.average_quiz_score}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'register' && (
        <div className="register-school-section">
          <h3>➕ Register New School</h3>
          {user ? (
            user.role === 'student' ? (
              <div className="access-denied">
                <h4>🚫 Access Denied</h4>
                <p>Students cannot create schools. You can only view your assigned school.</p>
                <p>Please contact your teacher or school administrator if you need assistance.</p>
              </div>
            ) : (
              <SchoolRegistrationForm 
                onSuccess={(data: any) => {
                  fetchSchools();
                  setActiveTab('schools');
                  showSchoolRegistrationDialog(data);
                }}
                onNotification={onNotification}
              />
            )
          ) : (
            <div className="login-required">
              <p>🔐 Please <strong>login or register</strong> to create a new school.</p>
              <p>You need to be logged in to register schools and become a school administrator.</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="school-analytics-section">
          <h3>📊 School System Analytics</h3>
          <div className="system-stats">
            <div className="stat-card">
              <h4>Total Schools</h4>
              <div className="stat-value">{schools.length}</div>
            </div>
            <div className="stat-card">
              <h4>Active Schools</h4>
              <div className="stat-value">{schools.filter(s => s.is_active).length}</div>
            </div>
            <div className="stat-card">
              <h4>Total Capacity</h4>
              <div className="stat-value">{schools.reduce((sum, s) => sum + s.max_students, 0)}</div>
            </div>
          </div>
          
          <div className="schools-overview">
            <h4>Schools Overview</h4>
            <div className="schools-list">
              {schools.map((school) => (
                <div key={school.id} className="school-overview-item">
                  <div className="school-basic-info">
                    <h5>{school.name}</h5>
                    <p>{school.city}, {school.country}</p>
                  </div>
                  <div className="school-stats">
                    <span>Est. {school.established_year}</span>
                    <span>Capacity: {school.max_students}</span>
                    <span className={`status ${school.is_active ? 'active' : 'inactive'}`}>
                      {school.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* School Registration Success Dialog */}
      {showRegistrationDialog && registrationData && (
        <div className="registration-dialog-overlay">
          <div className="registration-dialog">
            <div className="dialog-header">
              <h3>🎉 School Registered Successfully!</h3>
            </div>
            <div className="dialog-content">
              <p><strong>School:</strong> {registrationData.school?.name}</p>
              <p><strong>Teacher Email:</strong> {registrationData.teacher?.email}</p>
              <p><strong>Teacher Password:</strong> {registrationData.teacher?.password}</p>
              
              <div className="dialog-instructions">
                <h4>📋 Next Steps:</h4>
                <ol>
                  <li>Log out from your current account</li>
                  <li>Login using the teacher email and password above</li>
                  <li>You can now manage students for your school</li>
                </ol>
              </div>
              
              <div className="dialog-timer">
                <p>⏱️ This dialog will close automatically in 5 seconds...</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// School Registration Form Component
function SchoolRegistrationForm({ onSuccess, onNotification }: {
  onSuccess: (data: any) => void;
  onNotification: (type: 'success' | 'error', message: string) => void;
}) {
  const [schoolData, setSchoolData] = useState({
    school_name: '',
    school_type: 'high',
    address: '',
    city: '',
    state: '',
    country: '',
    phone: '',
    email: '',
    principal_name: '',
    established_year: '',
    max_students: '',
    max_teachers: ''
  });

  const [teacherData, setTeacherData] = useState({
    name: '',
    email: '',
    password: '',
    phone: ''
  });

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    // Validate required fields
    if (!schoolData.school_name || !schoolData.address || !schoolData.city || 
        !schoolData.state || !schoolData.country || !schoolData.phone || 
        !schoolData.email || !schoolData.principal_name) {
      onNotification('error', 'Please fill in all required school information fields');
      setLoading(false);
      return;
    }

    if (!teacherData.name || !teacherData.email || !teacherData.password || !teacherData.phone) {
      onNotification('error', 'Please fill in all required teacher information fields');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${config.API_BASE_URL}/api/schools/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          school_data: schoolData,
          teacher_data: {
            ...teacherData,
            school_id: "temp_id" // Will be set by backend
          }
        }),
      });

      const data = await response.json();

      if (response.ok) {
        onSuccess(data);
        // Reset form
        setSchoolData({
          school_name: '',
          school_type: 'high',
          address: '',
          city: '',
          state: '',
          country: '',
          phone: '',
          email: '',
          principal_name: '',
          established_year: '',
          max_students: '',
          max_teachers: ''
        });
        setTeacherData({
          name: '',
          email: '',
          password: '',
          phone: ''
        });
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Failed to register school');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form">
      <div className="form-section">
        <h4>🏫 School Information</h4>
        <div className="form-row">
          <div className="form-group">
            <input
              type="text"
              placeholder="School Name *"
              value={schoolData.school_name}
              onChange={(e) => setSchoolData({...schoolData, school_name: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <select
              value={schoolData.school_type}
              onChange={(e) => setSchoolData({...schoolData, school_type: e.target.value})}
            >
              <option value="elementary">Elementary School</option>
              <option value="middle">Middle School</option>
              <option value="high">High School</option>
              <option value="university">University</option>
            </select>
          </div>
        </div>
        
        <div className="form-group">
            <input
              type="text"
              placeholder="Address *"
              value={schoolData.address}
              onChange={(e) => setSchoolData({...schoolData, address: e.target.value})}
              required
            />
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <input
              type="text"
              placeholder="City *"
              value={schoolData.city}
              onChange={(e) => setSchoolData({...schoolData, city: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              placeholder="State/Province *"
              value={schoolData.state}
              onChange={(e) => setSchoolData({...schoolData, state: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              placeholder="Country *"
              value={schoolData.country}
              onChange={(e) => setSchoolData({...schoolData, country: e.target.value})}
              required
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <input
              type="tel"
              placeholder="Phone Number *"
              value={schoolData.phone}
              onChange={(e) => setSchoolData({...schoolData, phone: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="email"
              placeholder="School Email *"
              value={schoolData.email}
              onChange={(e) => setSchoolData({...schoolData, email: e.target.value})}
              required
            />
          </div>
        </div>
        
        <div className="form-group">
          <input
            type="text"
            placeholder="Principal Name *"
            value={schoolData.principal_name}
            onChange={(e) => setSchoolData({...schoolData, principal_name: e.target.value})}
            required
          />
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <input
              type="number"
              placeholder="Established Year (Optional)"
              value={schoolData.established_year}
              onChange={(e) => setSchoolData({...schoolData, established_year: e.target.value})}
              min="1800"
              max={new Date().getFullYear()}
            />
          </div>
          <div className="form-group">
            <input
              type="number"
              placeholder="Max Students (Optional)"
              value={schoolData.max_students}
              onChange={(e) => setSchoolData({...schoolData, max_students: e.target.value})}
              min="1"
            />
          </div>
          <div className="form-group">
            <input
              type="number"
              placeholder="Max Teachers (Optional)"
              value={schoolData.max_teachers}
              onChange={(e) => setSchoolData({...schoolData, max_teachers: e.target.value})}
              min="1"
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h4>👨‍🏫 School Teacher Information</h4>
        <div className="form-row">
          <div className="form-group">
            <input
              type="text"
              placeholder="Teacher Full Name *"
              value={teacherData.name}
              onChange={(e) => setTeacherData({...teacherData, name: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="email"
              placeholder="Teacher Email *"
              value={teacherData.email}
              onChange={(e) => setTeacherData({...teacherData, email: e.target.value})}
              required
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <input
              type="password"
              placeholder="Teacher Password *"
              value={teacherData.password}
              onChange={(e) => setTeacherData({...teacherData, password: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="tel"
              placeholder="Teacher Phone *"
              value={teacherData.phone}
              onChange={(e) => setTeacherData({...teacherData, phone: e.target.value})}
              required
            />
          </div>
        </div>
      </div>

      <button type="submit" className="btn btn-success" disabled={loading}>
        {loading ? 'Registering School...' : '🏫 Register School'}
      </button>
    </form>
  );
}

// Landing Page Component
function LandingPage({ onAppMode }: {
  onAppMode: (mode: 'guest' | 'user') => void;
}) {
  return (
    <div className="landing-page">
      <div className="landing-container">
        <div className="landing-header">
          <h1>🎓 AI-Powered Quiz System</h1>
          <p>Welcome to the future of education</p>
          <p>Choose how you'd like to continue:</p>
        </div>
        
        <div className="landing-options">
          <div className="landing-option">
            <div className="option-icon">👤</div>
            <h3>Continue as Guest</h3>
            <p>Create quizzes, take tests, and view results without creating an account</p>
            <button 
              className="btn btn-primary"
              onClick={() => onAppMode('guest')}
            >
              Continue as Guest
            </button>
          </div>
          
          <div className="landing-option">
            <div className="option-icon">🔐</div>
            <h3>Continue as User</h3>
            <p>Create an account to save progress, create quizzes, and access all features</p>
            <button 
              className="btn btn-success"
              onClick={() => onAppMode('user')}
            >
              Continue as User
            </button>
          </div>
        </div>
        
        <div className="landing-features">
          <h3>🌟 Features</h3>
          <div className="features-grid">
            <div className="feature-item">
              <span className="feature-icon">🤖</span>
              <span>AI-Generated Quizzes</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🏫</span>
              <span>School Management</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📊</span>
              <span>Analytics & Reports</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📱</span>
              <span>Mobile Friendly</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Student Management Component for Teachers
function StudentManagement({ user, onNotification }: {
  user: User;
  onNotification: (type: 'success' | 'error', message: string) => void;
}) {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newStudent, setNewStudent] = useState({
    name: '',
    email: '',
    password: ''
  });

  const fetchStudents = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/teachers/${user.id}/students`);
      const data = await response.json();
      
      if (response.ok) {
        setStudents(data.students || []);
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Failed to fetch students');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchStudents();
  }, []);

  const handleCreateStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newStudent.name || !newStudent.email || !newStudent.password) {
      onNotification('error', 'Please fill in all fields');
      return;
    }

    if (!user.school_id) {
      onNotification('error', 'Teacher must be associated with a school. Please register a school first or contact super admin.');
      return;
    }

    try {
      const requestData = {
        ...newStudent,
        school_id: user.school_id,
        teacher_id: user.id
      };
      
      console.log('Creating student with data:', requestData);
      console.log('User object:', user);
      
      const response = await fetch(`${config.API_BASE_URL}/api/teachers/create-student', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (response.ok) {
        onNotification('success', 'Student account created successfully!');
        setNewStudent({ name: '', email: '', password: '' });
        setShowCreateForm(false);
        fetchStudents();
      } else {
        onNotification('error', formatErrorMessage(data.detail) || 'Failed to create student account');
      }
    } catch (error) {
      onNotification('error', 'Error connecting to server');
    }
  };

  if (loading) {
    return (
      <div className="page">
        <h2>👥 Manage Students</h2>
        <div className="loading">Loading students...</div>
      </div>
    );
  }

  if (!user.school_id) {
    return (
      <div className="page">
        <h2>👥 Manage Students</h2>
        <div className="no-school-message">
          <h3>⚠️ No School Associated</h3>
          <p>You are not associated with any school yet.</p>
          <p>Please register a new school to get started.</p>
          <div className="action-buttons">
            <button 
              className="btn btn-primary"
              onClick={() => window.location.href = '#school-management'}
            >
              🏫 Go to School Management
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h2>👥 Manage Students</h2>
      <p>Create and manage student accounts for your school</p>
      
      <div className="student-management">
        <div className="management-header">
          <h3>Your Students ({students.length})</h3>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Cancel' : '➕ Create New Student'}
          </button>
        </div>

        {showCreateForm && (
          <div className="create-student-form">
            <h4>Create New Student Account</h4>
            <form onSubmit={handleCreateStudent} className="form">
              <div className="form-row">
                <div className="form-group">
                  <input
                    type="text"
                    placeholder="Student Name *"
                    value={newStudent.name}
                    onChange={(e) => setNewStudent({...newStudent, name: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <input
                    type="email"
                    placeholder="Student Email *"
                    value={newStudent.email}
                    onChange={(e) => setNewStudent({...newStudent, email: e.target.value})}
                    required
                  />
                </div>
              </div>
              <div className="form-group">
                <input
                  type="password"
                  placeholder="Student Password *"
                  value={newStudent.password}
                  onChange={(e) => setNewStudent({...newStudent, password: e.target.value})}
                  required
                />
              </div>
              <button type="submit" className="btn btn-success">
                Create Student Account
              </button>
            </form>
          </div>
        )}

        <div className="students-list">
          {students.length === 0 ? (
            <div className="no-students">
              <p>No students created yet. Create your first student account!</p>
            </div>
          ) : (
            <div className="students-grid">
              {students.map((student) => (
                <div key={student.id} className="student-card">
                  <div className="student-info">
                    <h4>{student.name}</h4>
                    <p><strong>Email:</strong> {student.email}</p>
                    <p><strong>Password:</strong> {student.password}</p>
                    <p><strong>Created:</strong> {new Date(student.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="student-actions">
                    <button className="btn btn-secondary" onClick={() => {
                      navigator.clipboard.writeText(`Email: ${student.email}\nPassword: ${student.password}`);
                      onNotification('success', 'Credentials copied to clipboard!');
                    }}>
                      📋 Copy Credentials
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;