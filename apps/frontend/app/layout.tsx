import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import { AppNav } from "@/components/AppNav";

export const metadata: Metadata = {
  title: "TrustGateAI",
  description: "AI testing and governance control plane",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppNav />
        <main className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
