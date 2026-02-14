import { Navbar } from "@/components/layout/Navbar";
import { Hero } from "@/components/home/Hero";
import { ApplicationsGrid } from "@/components/home/ApplicationsGrid";
import { Footer } from "@/components/layout/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-background relative selection:bg-primary/30">
        {/* Global Background Elements */}
        <div className="fixed inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" pointer-events-none />
        
        <Navbar />
        
        <div className="relative z-10">
            <Hero />
            <ApplicationsGrid />
        </div>

        <Footer />
    </main>
  );
}
