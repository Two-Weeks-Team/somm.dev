"use client";

import { useAuth } from "@/contexts/AuthContext";
import { ReAuthModal } from "./ReAuthModal";

export const AuthWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { showReAuthModal, closeReAuthModal } = useAuth();

  return (
    <>
      {children}
      <ReAuthModal isOpen={showReAuthModal} onClose={closeReAuthModal} />
    </>
  );
};
