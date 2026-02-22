import "./globals.css";
import "katex/dist/katex.min.css";
import "highlight.js/styles/github.css";

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/AppSideBar"



const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "tinyRAG",
  description: "Local first RAG agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <SidebarProvider>
          <AppSidebar />
          <main className="w-full h-svh min-h-0 flex flex-col overflow-hidden">
            <div className="shrink-0 p-2 border-b bg-background z-20">
              <SidebarTrigger className="z-30 relative"/>
            </div>
            <div className="flex-1 min-h-0 overflow-hidden">
              {children}
            </div>
          </main>
            
        </SidebarProvider>
      </body>
    </html>
    
  );
}
