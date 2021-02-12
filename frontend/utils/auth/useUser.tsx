import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { HOME_ROUTE, LOGIN_ROUTE } from "../routes";
import initFirebase from "./initFirebase";
import firebase from "firebase/app";
import "firebase/auth";
import { mapUserData } from "./mapUserData";
import {
  getUserFromCookie,
  removeUserCookie,
  setUserCookie,
} from "./userCookies";
import { DEFAULT_ERR_MESSAGE, DEFAULT_SIGN_IN_ERR_MESSAGE } from "../constants";
import { IUser } from "../../types/user";

initFirebase();

const useUser = () => {
  const [user, setUser] = useState<IUser | undefined>(undefined);
  const router = useRouter();

  const emailSignUp = async (
    email: string,
    password: string,
    errCallback: Function,
    finallyCallback: Function
  ) => {
    firebase
      .auth()
      .createUserWithEmailAndPassword(email, password)
      .then((res) => {
        res.user.sendEmailVerification();
        router.push(LOGIN_ROUTE);
      })
      .catch((error) => {
        console.log(error);
        return errCallback({
          error: true,
          message: error.message,
        });
      })
      .finally(() => finallyCallback(false));
  };

  const emailSignIn = async (
    email: string,
    password: string,
    errCallback: Function,
    finallyCallback: Function
  ) => {
    firebase
      .auth()
      .signInWithEmailAndPassword(email, password)
      .then((res) => {
        console.log(res);
        // router.push(HOME_ROUTE);
      })
      .catch((error) => {
        return errCallback({
          error: true,
          message: error.message,
        });
      })
      .finally(() => finallyCallback(false));
  };

  const logout = async () => {
    return firebase
      .auth()
      .signOut()
      .then(() => router.push(LOGIN_ROUTE))
      .catch((err) => {
        alert("Unable to log you out. Please try again.");
      });
  };

  useEffect(() => {
    const cancelAuthListener = firebase.auth().onIdTokenChanged((user) => {
      if (user) {
        const userData = mapUserData(user);
        setUserCookie(userData);
        setUser(userData);
      } else {
        removeUserCookie();
        setUser(undefined);
      }
    });

    const userFromCookie = getUserFromCookie();
    if (!userFromCookie) {
      return;
    }
    setUser(userFromCookie);

    return () => {
      cancelAuthListener();
    };

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { user, logout, emailSignIn, emailSignUp };
};

export { useUser };
