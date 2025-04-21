import Link from "next/link";
import React from "react";
import { Input } from "@/components/ui/input"; // Corrected path assumption
import { Button } from "@/components/ui/button"; // Corrected casing assumption
import { Bell, Menu, Search, Settings, Star, UserCircle } from "lucide-react"; // Example icons

const Header = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center justify-between px-4">
        {/* Left Side: Logo & Nav */}
        <div className="flex items-center gap-6 lg:gap-10">
          <Link href="/" className="flex items-center space-x-2">
            {/* Replace with actual Logo Component/SVG */}
            <span className="font-bold text-lg">TV</span> 
            {/* <span className="hidden font-bold sm:inline-block">WealthOS</span> */}
          </Link>
          <nav className="hidden items-center gap-6 text-sm md:flex">
            <Link
              href="/products"
              className="text-foreground/70 transition-colors hover:text-foreground"
            >
              Products
            </Link>
            <Link
              href="/community"
              className="text-foreground/70 transition-colors hover:text-foreground"
            >
              Community
            </Link>
            <Link
              href="/markets"
              className="font-medium text-foreground transition-colors hover:text-foreground"
            >
              Markets
            </Link>
            <Link
              href="/brokers"
              className="text-foreground/70 transition-colors hover:text-foreground"
            >
              Brokers
            </Link>
             <Link
              href="/more"
              className="text-foreground/70 transition-colors hover:text-foreground"
            >
              More
            </Link>
          </nav>
        </div>

        {/* Right Side: Search, Actions, User */}
        <div className="flex items-center gap-4">
          {/* Search Input (Placeholder) */}
          <div className="relative hidden sm:block">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search (⌘K)" // Cmd+K is common
              className="pl-8 sm:w-[200px] md:w-[250px] lg:w-[300px] h-9"
            />
          </div>

          {/* Action Icons (Placeholders) */}
           <Button variant="ghost" size="icon" className="hidden md:inline-flex">
            <Star className="h-5 w-5 text-foreground/70" />
            <span className="sr-only">Watchlist</span>
          </Button>
          <Button variant="ghost" size="icon" className="hidden md:inline-flex">
            <Bell className="h-5 w-5 text-foreground/70" />
            <span className="sr-only">Notifications</span>
          </Button>

          {/* Upgrade Button (Placeholder) - Check if size='sm' is valid */}
          <Button size="sm" className="hidden lg:inline-flex bg-blue-600 hover:bg-blue-700 text-white rounded-full px-3">
            Upgrade now
          </Button>

          {/* User Menu / Avatar (Placeholder) */}
          <Button variant="ghost" size="icon" className="rounded-full">
            {/* Replace with actual Avatar component or initials */}
             <UserCircle className="h-6 w-6 text-foreground/70" />
            <span className="sr-only">User Menu</span>
          </Button>
          
           {/* Settings/More Icon (Placeholder) */}
           <Button variant="ghost" size="icon" className="hidden md:inline-flex">
            <Settings className="h-5 w-5 text-foreground/70" />
            <span className="sr-only">Settings</span>
          </Button>

          {/* Mobile Menu Trigger */}
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle Menu</span>
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header; 