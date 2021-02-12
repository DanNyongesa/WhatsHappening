import { Alert } from "@material-ui/lab";
import Head from "next/head";
import Link from "next/link";
import React, { useState } from "react";
import AuthContainer from "../components/AuthContainer";
import { useUser } from "../utils/auth/useUser";

const Login: React.FC = () => {
  const { emailSignIn } = useUser();
  const [loggingIn, setLoggingIn] = useState(false);
  const [loggingErr, setLoggingErr] = useState({
    error: false,
    message: "",
  });
  const [loginDetails, setLoginDetails] = useState({
    email: "",
    password: "",
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setLoginDetails({ ...loginDetails, [e.target.name]: e.target.value });


  const loginWithEmail = (e: React.FormEvent) => {
    e.preventDefault();

    setLoggingErr({
      error: false,
      message: "",
    });
    setLoggingIn(true);

    const { email, password } = loginDetails;
    emailSignIn(email, password, setLoggingErr, setLoggingIn);
  };
  return (
    <>
      <Head>
        <title>Login</title>
      </Head>
      <AuthContainer pageTitle="Sign In">
        <form className="grid gap-3" onSubmit={loginWithEmail}>
          {loggingErr.error && (
            <Alert severity="error">{loggingErr.message}</Alert>
          )}
          <input
            required
            type="email"
            name="email"
            id="email"
            placeholder="Email Address"
            className="py-3 px-2 border-black rounded-sm border-2 w-auto"
            value={loginDetails.email}
            onChange={handleInputChange}
          />
          <input
            required
            type="password"
            name="password"
            id="password"
            placeholder="*********"
            className="py-3 px-2 border-black rounded-sm border-2"
            value={loginDetails.password}
            onChange={handleInputChange}
          />
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white py-3 px-2 uppercase text-base rounded-sm transition-all duration-300 text-center grid place-items-center"
            disabled={loggingIn}
          >
            {loggingIn ? (
              <img src="/images/spinner.gif" alt="" className="h-6" />
            ) : (
              "sign in"
            )}
          </button>
          <Link href="/register">
            <a className="text-sm text-gray-500 hover:text-gray-700 transition-all duration-3000">
              Dont have an account? Register.
            </a>
          </Link>
        </form>
      </AuthContainer>
    </>
  );
};

export default Login;
