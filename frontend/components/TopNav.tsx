"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function TopNav() {
  const pathname = usePathname();

  const linkClass = (path: string) =>
    `px-4 py-2 rounded-lg transition font-medium
     ${
       pathname === path
         ? "text-white bg-blue-600 shadow-lg shadow-blue-600/20"
         : "text-gray-300 hover:text-white hover:bg-blue-600/20"
     }`;

  return (
    <nav className="w-full bg-[#0a0f1a] border-b border-[#1d263b] px-8 py-4 flex items-center justify-between shadow-lg sticky top-0 z-50">
      
      {/* LEFT SIDE — Branding */}
      <div className="text-xl font-bold text-blue-400 tracking-wide">
        GDPR Privacy Firewall
      </div>

      {/* RIGHT SIDE — Nav Links */}
      <div className="flex gap-4 items-center">
        <Link href="/" className={linkClass("/")}>
          Firewall
        </Link>

        <Link href="/history" className={linkClass("/history")}>
          Dashboard
        </Link>

        <Link href="/settings" className={linkClass("/settings")}>
          Settings
        </Link>
      </div>
    </nav>
  );
}
