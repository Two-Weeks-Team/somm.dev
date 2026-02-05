import React, { Suspense } from "react";

import AuthCallbackClient from "./AuthCallbackClient";

export default function AuthCallbackPage() {
  return (
    <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center px-4">
      <Suspense
        fallback={
          <div className="w-full max-w-md rounded-xl border border-gray-100 bg-white p-6 text-center shadow-sm">
            <h1 className="text-2xl font-bold text-[#722F37] font-serif">
              Signing you in
            </h1>
            <p className="mt-3 text-gray-600">Please wait...</p>
          </div>
        }
      >
        <AuthCallbackClient />
      </Suspense>
    </div>
  );
}
