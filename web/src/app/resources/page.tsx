'use client';

import { useEffect } from 'react';

export default function ResourcesPage() {
  useEffect(() => {
    window.location.href = 'https://blockaccesslist.xyz/';
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 font-mono relative flex items-center justify-center">
      <div className="text-center">
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Redirecting to Resources...
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Taking you to <span className="text-lime-500">blockaccesslist.xyz</span>
          </p>
        </div>
        <div className="w-6 h-6 border-2 border-lime-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      </div>
    </div>
  );
}
