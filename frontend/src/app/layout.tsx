import type { Metadata } from "next";
import Providers from "@/components/Providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Intelli-Credit - AI-Powered Credit Appraisal",
  description:
    "Integrated credit assessment platform using Knowledge Graphs for Five C's analysis, shell company detection, and ITC reconciliation",
  icons: {
    icon: "/intelli-credit-logo.png",
    apple: "/intelli-credit-logo.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="min-h-screen c-bg-main">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
