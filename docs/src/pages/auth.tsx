import React, { useState } from 'react';
import Layout from '@theme/Layout';
import BrowserOnly from '@docusaurus/BrowserOnly';
import LoginForm from '@site/src/components/Auth/LoginForm';
import SignupForm from '@site/src/components/Auth/SignupForm';

export default function AuthPage() {
  return (
    <Layout
      title="Authentication"
      description="Login or Sign up to your account"
    >
      <BrowserOnly fallback={<div style={{ textAlign: 'center', padding: '4rem 2rem' }}>Loading...</div>}>
        {() => <AuthContent />}
      </BrowserOnly>
    </Layout>
  );
}

function AuthContent() {
  // Check URL parameter to determine initial form
  const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
  const initialMode = urlParams?.get('mode') === 'signup' ? false : true; // default to login

  const [showLogin, setShowLogin] = useState(initialMode);
  const { useSession } = require('@site/src/utils/authClient');
  const { data: session, isPending } = useSession();

  // If user is already logged in, redirect or show logged-in state
  if (isPending) {
    return (
      <Layout title="Authentication" description="Login or Sign up">
        <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <p>Loading...</p>
        </div>
      </Layout>
    );
  }

  if (session) {
    return (
      <Layout title="Authentication" description="Login or Sign up">
        <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <h1>Welcome, {session.user.name}!</h1>
          <p>You are already logged in.</p>
          <a href="/">Go to Home</a>
        </div>
      </Layout>
    );
  }

  const handleSuccess = () => {
    // Redirect to home page or dashboard after successful auth
    window.location.href = '/';
  };

  return (
    <>
      {showLogin ? (
        <LoginForm
          onSuccess={handleSuccess}
          onSwitchToSignup={() => setShowLogin(false)}
        />
      ) : (
        <SignupForm
          onSuccess={handleSuccess}
          onSwitchToLogin={() => setShowLogin(true)}
        />
      )}
    </>
  );
}
