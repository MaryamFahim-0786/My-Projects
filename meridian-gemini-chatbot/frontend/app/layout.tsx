import type { Metadata } from "next";
import { Inter, Newsreader } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const newsreader = Newsreader({ subsets: ["latin"], variable: "--font-newsreader", style: ["italic", "normal"] });

export const metadata: Metadata = {
  title: "Meridian — Gemini Chat",
  description: "An advanced Gemini-powered assistant with memory, document search, and live tools.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${newsreader.variable}`}>
      <body className="bg-ink text-paper font-sans antialiased">{children}</body>
    </html>
  );
}
