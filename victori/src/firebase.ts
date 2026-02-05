// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyD43ymhxOztD1_ceggq3oo-GSw4DhHU9JU",
  authDomain: "victori-6e826.firebaseapp.com",
  databaseURL: "https://victori-6e826-default-rtdb.firebaseio.com",
  projectId: "victori-6e826",
  storageBucket: "victori-6e826.firebasestorage.app",
  messagingSenderId: "166916157817",
  appId: "1:166916157817:web:dea76b1c99bd0ef00f3fa8",
  measurementId: "G-XKPWNDK39R"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
getAnalytics(app);