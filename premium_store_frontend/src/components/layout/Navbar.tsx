"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, Search, ShoppingCart, User, X } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-background/80 backdrop-blur-md">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-400 bg-clip-text text-transparent hover:opacity-80 transition-opacity">
          PremiumStore
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          <Link href="/" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
            Home
          </Link>
          <Link href="/services" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
            Services
          </Link>
          <Link href="/about" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
            About
          </Link>
        </div>

        {/* Actions */}
        <div className="hidden md:flex items-center space-x-4">
          <Button variant="ghost" size="icon" className="hover:text-primary hover:bg-white/5">
            <Search className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" className="hover:text-primary hover:bg-white/5 relative">
            <ShoppingCart className="h-5 w-5" />
            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-primary" />
          </Button>
          <Button variant="ghost" size="icon" className="hover:text-primary hover:bg-white/5">
            <User className="h-5 w-5" />
          </Button>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden p-2 text-muted-foreground hover:text-primary"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden border-t border-white/10 bg-background">
          <div className="container mx-auto px-4 py-4 space-y-4">
            <Link
              href="/"
              className="block text-sm font-medium text-muted-foreground hover:text-primary"
              onClick={() => setIsOpen(false)}
            >
              Home
            </Link>
            <Link
              href="/services"
              className="block text-sm font-medium text-muted-foreground hover:text-primary"
              onClick={() => setIsOpen(false)}
            >
              Services
            </Link>
            <Link
              href="/about"
              className="block text-sm font-medium text-muted-foreground hover:text-primary"
              onClick={() => setIsOpen(false)}
            >
              About
            </Link>
            <div className="flex items-center space-x-4 pt-4 border-t border-white/10">
              <Button variant="ghost" size="sm" className="w-full justify-start hover:text-primary">
                <Search className="h-4 w-4 mr-2" /> Search
              </Button>
              <Button variant="ghost" size="sm" className="w-full justify-start hover:text-primary">
                <ShoppingCart className="h-4 w-4 mr-2" /> Cart
              </Button>
              <Button variant="ghost" size="sm" className="w-full justify-start hover:text-primary">
                <User className="h-4 w-4 mr-2" /> Account
              </Button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
