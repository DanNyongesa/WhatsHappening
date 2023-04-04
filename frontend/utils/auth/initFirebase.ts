// Firebase App (the core Firebase SDK) is always required and must be listed first
import firebase from "firebase/app";

// Add the Firebase products that you want to use
import "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDLOFq2cdvu9g20weGh6Idu57xaz1owFZs",
  authDomain: "meemlawds.firebaseapp.com",
  databaseURL: "https://meemlawds.firebaseio.com",
  projectId: "meemlawds",
  storageBucket: "meemlawds.appspot.com",
  messagingSenderId: "926841500383",
  appId: "1:926841500383:web:1e38f1ad145c4876ca6f6a",
  measurementId: "G-ZKQ00MS7KG",
};

const initFirebase = () => {
  if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
  }
};

export default initFirebase;
