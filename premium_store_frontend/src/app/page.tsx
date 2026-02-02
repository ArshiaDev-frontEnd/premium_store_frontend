"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api } from "@/lib/api/client";

interface Application {
  name: string; // The serializer returns 'title' but backend model says 'title', wait. Serializer says 'title', but slug related field 'top_service'? 
  // Let's check serializer: ApplicationSerializer -> fields = ["title", "description", "top_service", "image", "image_url"]
  title: string;
  description: string;
  image_url: string;
  id?: number; // Serializer default doesn't show ID? Let's check. ModelSerializer includes ID by default?
  // ApplicationSerializer Meta fields doesn't include "id"! This is a backend issue or a feature?
  // Let's check API_DOCUMENTATION.md
}

// Documentation says:
// GET /applications/ -> List/create applications.
// GET /applications/<id>/ -> Details
// If ID is not in serializer, how do we link?
// Checking ApplicationSerializer in Step 36 lines 18-20: fields = ["title", "description", "top_service", "image", "image_url"]
// ID IS MISSING! This is a backend bug or I need to use title as slug?
// Wait, URLs.py would tell us. "browse applications (categories)".
// I'll assume for now I need to modify backend or use title? 
// Actually, usually ModelSerializer includes 'id' if not excluded, but if `fields` is explicit list, it must act explicit.
// Step 36: fields = ["title", "description", "top_service", "image", "image_url"]
// Yes, ID is missing. The user might need me to fix backend too?
// But documentation says GET /applications/<pk>/services/.
// So I definitely need ID (pk).

// I will PATCH the backend serializer to include "id".
// This is "Advanced Engineering" -> identifying backend bugs.

export default function Home() {
  const [apps, setApps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/applications/")
      .then((res) => {
        setApps(res.data.results || res.data);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <main className="min-h-screen p-8 bg-background">
      <div className="container mx-auto space-y-8">
        <section className="text-center space-y-4">
          <h1 className="text-5xl font-extrabold tracking-tight lg:text-6xl text-gradient">
            Premium Services <br /> <span className="text-primary">Instantly.</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Upgrade your digital lifestyle with instant access to premium subscriptions.
            Secure, fast, and verified.
          </p>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {apps.map((app, idx) => (
            <Card key={idx} className="hover:border-primary/50 transition-colors cursor-pointer group">
              <CardHeader>
                {/* Image would go here if we had Next/Image setup for external */}
                <div className="aspect-video w-full overflow-hidden rounded-md bg-muted relative mb-4">
                    {app.image_url ? (
                        <img src={app.image_url} alt={app.title} className="object-cover w-full h-full group-hover:scale-105 transition-transform" />
                    ) : (
                        <div className="flex items-center justify-center h-full text-muted-foreground">No Image</div>
                    )}
                </div>
                <CardTitle>{app.title}</CardTitle>
                <CardDescription className="line-clamp-2">{app.description}</CardDescription>
              </CardHeader>
              <CardFooter>
                  {/* Since ID is missing, I can't link yet. I will fix backend. */}
                  <Button variant="secondary" className="w-full">View Services</Button>
              </CardFooter>
            </Card>
          ))}
        </section>
      </div>
    </main>
  );
}
