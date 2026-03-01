// app/layout.tsx
import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Information Manager Dashboard",
  description: "A secure interface for viewing sanitized data",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-gray-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
