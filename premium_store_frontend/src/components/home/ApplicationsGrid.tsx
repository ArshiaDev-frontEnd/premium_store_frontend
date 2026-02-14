"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { Loader2, ArrowRight } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Application {
  id: number;
  title: string;
  description: string;
  image_url: string;
  top_service: string;
}

export function ApplicationsGrid() {
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/applications/")
      .then((res) => {
        setApps(res.data.results || res.data);
      })
      .catch((err) => {
        console.error("Backend unavailable, using mock data", err);
        // Fallback Mock Data
        setApps([
            { id: 1, title: "Spotify Premium", description: "Ad-free music listening with offline playback.", image_url: "", top_service: "spotify" },
            { id: 2, title: "Netflix 4K", description: "Watch movies and TV shows in Ultra HD.", image_url: "", top_service: "netflix" },
            { id: 3, title: "ChatGPT Plus", description: "Access to GPT-4 and faster response speeds.", image_url: "", top_service: "chatgpt" },
            { id: 4, title: "Apple Music", description: "Stream over 100 million songs ad-free.", image_url: "", top_service: "apple-music" },
            { id: 5, title: "YouTube Premium", description: "Ad-free YouTube and YouTube Music.", image_url: "", top_service: "youtube" },
            { id: 6, title: "PlayStation Plus", description: "Online multiplayer, monthly games, and more.", image_url: "", top_service: "ps-plus" },
        ]);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <section className="py-20 bg-black/20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold mb-4">
            Available <span className="text-primary">Services</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Choose from our wide range of premium services. Instant delivery guaranteed.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {apps.map((app) => (
            <Card 
              key={app.id} 
              className="group relative overflow-hidden border-white/5 bg-white/5 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:shadow-[0_0_30px_rgba(var(--primary),0.2)]"
            >
              {/* Gradient Borders on Hover */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

              <div className="aspect-video w-full overflow-hidden bg-black/50 relative">
                 {app.image_url ? (
                    <img 
                      src={app.image_url} 
                      alt={app.title} 
                      className="object-cover w-full h-full group-hover:scale-110 transition-transform duration-500" 
                    />
                 ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                        No Image Available
                    </div>
                 )}
                 {/* Overlay */}
                 <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <Button variant="secondary" className="translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                        View Details
                    </Button>
                 </div>
              </div>

              <CardHeader>
                <CardTitle className="text-xl group-hover:text-primary transition-colors">{app.title}</CardTitle>
                <div className="w-12 h-1 bg-primary rounded-full mb-2" />
                <CardDescription className="line-clamp-2 text-gray-400">
                    {app.description}
                </CardDescription>
              </CardHeader>
              
              <CardFooter className="pt-0">
                  <div className="flex items-center text-sm text-primary font-medium opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
                      Explore now <ArrowRight className="ml-1 w-4 h-4" />
                  </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
