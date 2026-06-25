import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "MindKeep",
  description: "Local-first AI workplace memory for SMEs",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="th">
      <body>{children}</body>
    </html>
  );
}
