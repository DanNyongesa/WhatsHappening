import { IUser } from "../../types/user";

export const mapUserData = (user: any): IUser => {
  const { uid, email, xa, displayName, photoURL } = user;
  return {
    id: uid,
    email,
    token: xa,
    displayName,
    photoURL,
  };
};
