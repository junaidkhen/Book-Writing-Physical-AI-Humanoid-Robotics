import { createAuthClient } from "better-auth/react";

/**
 * Get the auth service base URL based on environment
 *
 * IMPORTANT: After deploying the auth service to Vercel, update the production URL below
 * with your deployed auth service URL (e.g., https://your-auth-service.vercel.app)
 */
const getBaseURL = () => {
  if (typeof window !== 'undefined') {
    // Development: use local auth service
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return 'http://localhost:3001';
    }

    // Production: Deployed auth service URL (aliased - stable across deployments)
    return 'https://auth-service-self-alpha.vercel.app';
  }

  // Fallback for SSR
  return "http://localhost:3001";
};

export const authClient = createAuthClient({
  baseURL: getBaseURL(),
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
} = authClient;
