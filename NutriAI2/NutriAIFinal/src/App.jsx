import { useState } from 'react';
import './App.css';
import Personalization from './components/Personalization';
import SignupLogin from './components/SignupLogin';
import logo from './assets/NutriAI.png';

function App() {
  // Simple auth gate: false = show login/signup, true = show app content.
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <main className="app-container">
      {/* App brand/logo shown in the corner on all screens. */}
      <img src={logo} alt="NutriAI logo" className="app-logo" />
      {/* Only allow access to personalization after successful auth. */}
      {isAuthenticated ? (
        <Personalization />
      ) : (
        <>
          {/* Child calls onAuthSuccess after a successful signup/login response. */}
          <SignupLogin onAuthSuccess={() => setIsAuthenticated(true)} />
        </>
      )}
    </main>
  );
}

export default App;
