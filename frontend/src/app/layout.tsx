import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "OneNexora AI | Content Workspace",
  description: "AI influencer content workspace.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body className={inter.className}><div className="min-h-screen bg-background text-foreground"><Sidebar /><main className="min-h-screen lg:ml-64"><div className="mx-auto w-full max-w-[1600px] p-4 pt-16 md:p-8 lg:p-10 lg:pt-10">{children}</div></main></div></body></html>;
}
