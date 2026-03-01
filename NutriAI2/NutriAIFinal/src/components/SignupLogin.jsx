import { useState } from 'react';
import './SignupLogin.css';

function SignupLogin({ onAuthSuccess }) {
    // Current screen mode in the same card.
    const [mode, setMode] = useState('signup');
    // Shared form state for signup/login fields.
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
    });

    // True when user is on signup tab, false on login tab.
    const isSignup = mode === 'signup';

    const handleChange = (event) => {
        const { name, value } = event.target;
        // Keep inputs controlled by React state.
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        // Hit different backend routes for signup vs login.
        const endpoint = isSignup ? '/api/auth/signup' : '/api/auth/login';
        // Login route expects only email/password; signup includes name too.
        const payload = isSignup
            ? formData
            : { email: formData.email, password: formData.password };

        // Send credentials to Flask backend.
        const response = await fetch(`http://localhost:5000${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        // Parse backend response body once for success/error handling.
        const data = await response.json();
        console.log(data);

        if (response.ok) {
            // Notify parent so App can unlock protected content.
            if (onAuthSuccess) onAuthSuccess(data);
            return;
        }

        alert(data.error || 'Authentication failed');
    };

    return (
        <section className="auth-card">
            <div className="auth-header">
                <h1>{isSignup ? 'Sign Up' : 'Login'}</h1>
                {/* Toggle between signup and login without leaving the page. */}
                <div className="auth-toggle">
                    <button
                        type="button"
                        className={isSignup ? 'active' : ''}
                        onClick={() => setMode('signup')}
                    >
                        Sign Up
                    </button>
                    <button
                        type="button"
                        className={!isSignup ? 'active' : ''}
                        onClick={() => setMode('login')}
                    >
                        Login
                    </button>
                </div>
            </div>

            <form className="auth-form" onSubmit={handleSubmit}>
                {/* Name is only needed when creating a new account. */}
                {isSignup && (
                    <label>
                        Name
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                        />
                    </label>
                )}

                <label>
                    Email
                    <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                </label>

                <label>
                    Password
                    <input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                </label>

                <button type="submit" className="submit-btn">
                    {isSignup ? 'Create Account' : 'Login'}
                </button>
            </form>
        </section>
    );
}

export default SignupLogin;
