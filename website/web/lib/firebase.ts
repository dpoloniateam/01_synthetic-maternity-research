import { initializeApp, getApps, getApp, type FirebaseApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";

const config = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
  projectId: process.env.NEXT_PUBLIC_PROJECT_ID!,
};

export const app: FirebaseApp = getApps().length ? getApp() : initializeApp(config);
export const auth: Auth = getAuth(app);
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api";
