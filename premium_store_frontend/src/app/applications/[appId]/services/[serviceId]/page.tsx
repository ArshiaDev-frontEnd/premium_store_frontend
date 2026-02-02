"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Loader2 } from "lucide-react";

import { ServiceForm } from "@/components/modules/ServiceForm";
import { api } from "@/lib/api/client";

interface Service {
  id: number;
  name: string;
  description: string;
  price: number;
  discounted_price: number | null;
  image_url: string;
  required_fields: any[]; // Defined in ServiceForm
}

export default function ServiceDetailsPage() {
  const params = useParams();
  const { appId, serviceId } = params; // Params might be named differently depending on folder naming?
  // Next.js params object uses the folder names in brackets.
  // Folder: src/app/applications/[appId]/services/[serviceId]/page.tsx
  // So params should be { appId: string, serviceId: string }
  
  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // We need to fetch from /applications/<appId>/services/<serviceId>/
    // Or just /applications/<appId>/services/ and filter?
    // DRF NestedRouter usually supports DETAIL view at /applications/<appId>/services/<serviceId>/
    if (appId && serviceId) {
       api.get(`/applications/${appId}/services/${serviceId}/`)
         .then((res) => setService(res.data))
         .catch((err) => {
             console.error(err);
             setError("Failed to load service details.");
         })
         .finally(() => setLoading(false));
    }
  }, [appId, serviceId]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !service) {
      return (
          <div className="flex min-h-screen items-center justify-center text-destructive">
              {error || "Service not found."}
          </div>
      )
  }

  return (
    <div className="container mx-auto p-8 space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Left Column: Image & Description */}
          <div className="space-y-6">
              <div className="aspect-video w-full bg-muted rounded-lg overflow-hidden relative shadow-lg">
                  {service.image_url ? (
                      <img src={service.image_url} alt={service.name} className="object-cover w-full h-full" />
                  ) : (
                      <div className="flex items-center justify-center h-full text-muted-foreground">No Image</div>
                  )}
              </div>
              <div>
                  <h1 className="text-4xl font-bold mb-2">{service.name}</h1>
                  <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                      {service.description}
                  </p>
              </div>
          </div>

          {/* Right Column: Order Form */}
          <div>
              <ServiceForm service={service} />
          </div>
      </div>
    </div>
  );
}
