import { betterAuth } from "better-auth";
import { PrismaClient } from "../generated/prisma";
import { prismaAdapter } from "better-auth/adapters/prisma";

// Initialize Prisma Client
const prisma = new PrismaClient();

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET || "HbB0LQgjv6FCmBzbxUon7MvjGyx2iuJv",
  baseURL: process.env.BETTER_AUTH_URL || "https://book-writing-physical-ai-humanoid-r.vercel.app/",

  // Database configuration with Prisma
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),

  // Email and Password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true in production
  },

  // Configure social providers (optional)
  // socialProviders: {
  //   google: {
  //     clientId: process.env.GOOGLE_CLIENT_ID!,
  //     clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  //   },
  //   github: {
  //     clientId: process.env.GITHUB_CLIENT_ID!,
  //     clientSecret: process.env.GITHUB_CLIENT_SECRET!,
  //   },
  // },
});

export { prisma };
