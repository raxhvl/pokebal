"use client";

import { useEffect } from "react";

export default function Home() {
  useEffect(() => {
    const redirectUrl = process.env.NEXT_PUBLIC_REDIRECT_URL;
    if (redirectUrl) {
      // Redirect after 2 seconds
      const timeout = setTimeout(() => {
        window.location.href = redirectUrl;
      }, 2000);

      return () => clearTimeout(timeout);
    }
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
      <div className="text-center space-y-4 p-8">
        <h1 className="text-4xl md:text-6xl font-bold">
          <span className="font-light">Poké</span>
          <span className="text-lime-500 font-bold">BAL</span>
        </h1>
        <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-400">
          is now part of{" "}
          <span className="text-lime-500 font-semibold">butterfly</span>
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-500 mt-8">
          Redirecting...
        </p>
      </div>
    </div>
  );
}
