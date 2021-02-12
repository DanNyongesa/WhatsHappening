import { Avatar } from "@material-ui/core";
import Link from "next/link";
import React from "react";

const TopAppbar = () => {
  return (
    <nav className="bg-white-700 py-4 shadow-md">
      <div className="container flex justify-between mx-auto items-center">
        <h6 className="text-lg text-purple-700">Dundaa</h6>
        <div className="flex items-center gap-12">
          <Link href="/">
            <a className="text-sm text-black uppercase transition-all duration-300 hover:text-opacity-70 font-medium">
              Home
            </a>
          </Link>
          <Link href="/events">
            <a className="text-sm text-black uppercase transition-all duration-300 hover:text-opacity-70 font-medium">
              All Events
            </a>
          </Link>
          <Avatar />
        </div>
      </div>
    </nav>
  );
};

export default TopAppbar;
