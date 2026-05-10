import type { ReactNode } from "react";

export const metadata = {
  title: "Synthetic Maternity IRR",
  description: "Coder elicitation for synthetic maternity research",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, sans-serif", maxWidth: 880, margin: "2rem auto", padding: "0 1rem", color: "#111", lineHeight: 1.5 }}>
        {children}
      </body>
    </html>
  );
}
