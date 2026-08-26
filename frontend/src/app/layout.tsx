import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Traffic Monitoring — Real-Time Computer Vision & SMP Analytics",
  description: "Real-time traffic load monitoring and counting system based on YOLOv11 and PKJI standards",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0a0d14] text-slate-100 antialiased selection:bg-emerald-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
