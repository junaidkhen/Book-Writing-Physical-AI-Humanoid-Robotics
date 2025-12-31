# Better Auth Components

This directory contains authentication components built with Better Auth for the Docusaurus site.

## Components

### 1. LoginForm
A complete login form with email/password authentication.

**Usage:**
```tsx
import LoginForm from '@site/src/components/Auth/LoginForm';

<LoginForm
  onSuccess={() => console.log('Logged in!')}
  onSwitchToSignup={() => setShowSignup(true)}
/>
```

**Props:**
- `onSuccess?: () => void` - Callback when login succeeds
- `onSwitchToSignup?: () => void` - Callback to switch to signup form

### 2. SignupForm
A complete signup form with name, email, and password fields.

**Usage:**
```tsx
import SignupForm from '@site/src/components/Auth/SignupForm';

<SignupForm
  onSuccess={() => console.log('Account created!')}
  onSwitchToLogin={() => setShowLogin(true)}
/>
```

**Props:**
- `onSuccess?: () => void` - Callback when signup succeeds
- `onSwitchToLogin?: () => void` - Callback to switch to login form

### 3. UserProfile
A navbar-ready user profile dropdown component.

**Usage:**
```tsx
import UserProfile from '@site/src/components/Auth/UserProfile';

// In your navbar
<UserProfile />
```

This component automatically:
- Shows "Log In" and "Sign Up" buttons when not authenticated
- Shows user avatar and dropdown menu when authenticated
- Provides sign out functionality

## Auth Client Utilities

The `authClient.ts` file provides React hooks and functions:

```tsx
import { useSession, signIn, signOut } from '@site/src/utils/authClient';

// In your component
function MyComponent() {
  const { data: session, isPending } = useSession();

  if (isPending) return <div>Loading...</div>;
  if (!session) return <div>Not logged in</div>;

  return (
    <div>
      <p>Welcome, {session.user.name}!</p>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  );
}
```

## Pages

### /auth
The main authentication page that toggles between login and signup forms.

Visit: `http://localhost:3000/auth`

## Integration with Navbar

To add the UserProfile component to your Docusaurus navbar, you'll need to swizzle the Navbar component:

```bash
npm run swizzle @docusaurus/theme-classic Navbar -- --wrap
```

Then import and add the UserProfile component to your navbar.

## Styling

All components use CSS modules for styling, which:
- Supports both light and dark themes
- Follows Docusaurus design tokens
- Is fully responsive

## Features

- ✅ Email/Password authentication
- ✅ Form validation
- ✅ Error handling
- ✅ Loading states
- ✅ Remember me functionality
- ✅ User session management
- ✅ Responsive design
- ✅ Dark mode support
- ✅ TypeScript support

## Next Steps

1. Set up your PostgreSQL database
2. Run Prisma migrations: `npx prisma migrate dev`
3. Configure environment variables
4. Optionally add social providers (Google, GitHub, etc.)
5. Customize styling to match your brand
