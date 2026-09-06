import "./globals.css";

export const metadata = {
  title: "Crypto AI Assistant",
  description: "Live crypto prices, charts, and an AI market assistant.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="font-body bg-terminal-bg text-terminal-text min-h-screen">
        {children}
      </body>
    </html>
  );
}
