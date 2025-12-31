import React, { useState } from 'react';
import { useSession, signOut } from '@site/src/utils/authClient';
import styles from './UserProfile.module.css';

export default function UserProfile() {
  const { data: session, isPending } = useSession();
  const [showDropdown, setShowDropdown] = useState(false);

  if (isPending) {
    return <div className={styles.loading}>Loading...</div>;
  }

  if (!session) {
    return (
      <div className={styles.authLinks}>
        <a href="/auth?mode=login" className={styles.loginLink}>
          Log In
        </a>
        <a href="/auth?mode=signup" className={styles.signupButton}>
          Sign Up
        </a>
      </div>
    );
  }

  const handleSignOut = async () => {
    await signOut();
    window.location.href = '/';
  };

  // Get user initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className={styles.userProfile}>
      <button
        className={styles.profileButton}
        onClick={() => setShowDropdown(!showDropdown)}
        onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
      >
        {session.user.image ? (
          <img
            src={session.user.image}
            alt={session.user.name || 'User'}
            className={styles.avatar}
          />
        ) : (
          <div className={styles.avatarPlaceholder}>
            {getInitials(session.user.name || 'User')}
          </div>
        )}
        <span className={styles.userName}>{session.user.name}</span>
      </button>

      {showDropdown && (
        <div className={styles.dropdown}>
          <div className={styles.dropdownHeader}>
            <p className={styles.dropdownName}>{session.user.name}</p>
            <p className={styles.dropdownEmail}>{session.user.email}</p>
          </div>
          <div className={styles.dropdownDivider} />
          <a href="/profile" className={styles.dropdownItem}>
            Profile Settings
          </a>
          <a href="/dashboard" className={styles.dropdownItem}>
            Dashboard
          </a>
          <div className={styles.dropdownDivider} />
          <button onClick={handleSignOut} className={styles.dropdownItem}>
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}
