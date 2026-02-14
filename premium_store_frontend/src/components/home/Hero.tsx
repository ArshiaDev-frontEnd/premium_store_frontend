import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function Hero() {
  return (
    <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-primary/20 blur-[120px] rounded-full opacity-50 pointer-events-none" />
      
      <div className="container mx-auto px-4 text-center relative z-10">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6">
          Premium Digital <br />
          <span className="bg-gradient-to-r from-primary via-cyan-400 to-blue-600 bg-clip-text text-transparent animate-gradient-x">
            Experience
          </span>
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
          Instant delivery of top-tier verified accounts and premium subscriptions. 
          Elevate your digital life with secure and seamless access.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button size="lg" className="h-12 px-8 text-lg rounded-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_20px_rgba(var(--primary),0.5)]">
            Explore Store <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button size="lg" variant="outline" className="h-12 px-8 text-lg rounded-full border-white/10 hover:bg-white/5 hover:text-white">
            View Features
          </Button>
        </div>
      </div>
    </section>
  );
}
