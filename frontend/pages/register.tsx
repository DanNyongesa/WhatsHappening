import { Alert } from "@material-ui/lab";
import Head from "next/head";
import Link from "next/link";
import React, { useState } from "react";
import AuthContainer from "../components/AuthContainer";
import { useUser } from "../utils/auth/useUser";

const Register: React.FC = () => {
  const { emailSignUp } = useUser();
  const [registering, setRegistering] = useState(false);
  const [registrationErr, setRegisterionErr] = useState({
    error: false,
    message: "",
  });
  const [registrationDetails, setRegistrationDetails] = useState({
    email: "",
    password: "",
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setRegistrationDetails({
      ...registrationDetails,
      [e.target.name]: e.target.value,
    });

  const register = (e: React.FormEvent) => {
    e.preventDefault();

    setRegisterionErr({
      error: false,
      message: "",
    });
    setRegistering(true);

    const { email, password } = registrationDetails;
    return emailSignUp(email, password, setRegisterionErr, setRegistering);
  };
  return (
    <>
      <Head>
        <title>Create Account</title>
      </Head>
      <AuthContainer pageTitle="Create Account">
        <form className="grid gap-3" onSubmit={register}>
          {registrationErr.error && (
            <Alert severity="error">{registrationErr.message}</Alert>
          )}
          <input
            required
            type="email"
            name="email"
            id="email"
            placeholder="Email Address"
            className="py-3 px-2 border-black rounded-sm border-2 w-auto"
            value={registrationDetails.email}
            onChange={handleInputChange}
          />
          <input
            required
            type="password"
            name="password"
            id="password"
            placeholder="*********"
            className="py-3 px-2 border-black rounded-sm border-2"
            value={registrationDetails.password}
            onChange={handleInputChange}
          />
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white py-3 px-2 uppercase text-base rounded-sm transition-all duration-300 text-center grid place-items-center"
            disabled={registering}
          >
            {registering ? (
              <img src="/images/spinner.gif" alt="" className="h-6" />
            ) : (
              "create account"
            )}
          </button>
          <Link href="/login">
            <a className="text-sm text-gray-500 hover:text-gray-700 transition-all duration-3000">
              Already have an account? Sign In.
            </a>
          </Link>
        </form>
      </AuthContainer>
    </>
  );
};

export default Register;
