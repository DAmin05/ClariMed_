import { initializeApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
} from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyA5d3ra-rUA3EIW2Pv3wcjPYM-bEk4aHLo",
  authDomain: "hackru-2025-ee45d.firebaseapp.com",
  projectId: "hackru-2025-ee45d",
  storageBucket: "hackru-2025-ee45d.firebasestorage.app",
  messagingSenderId: "501699255361",
  appId: "1:501699255361:web:3d57021cbdef71c449bac0",
  measurementId: "G-K4WB9DQSDD",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const provider = new GoogleAuthProvider();

export const loginWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, provider);
    console.log("✅ Logged in successfully", result.user);
    return result.user;
  } catch (error) {
    console.error("❌ Login error", error);
  }
};

export const logout = async () => {
  try {
    await signOut(auth);
  } catch (error) {
    console.error("❌ Logout error", error);
  }
};

export const observeUser = (callback) => {
  return onAuthStateChanged(auth, callback);
};
