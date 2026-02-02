"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import Link from "next/link"; // Ensure this import creates a link, even if types fail temporarily

import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api } from "@/lib/api/client";

interface Service {
  id: number;
  name: string;
  description: string;
  price: number;
  discounted_price: number | null;
  image_url: string;
}

export default function ApplicationServicesPage() {
  const params = useParams();
  const applicationId = params.id;
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (applicationId) {
      api.get(`/applications/${applicationId}/services/`)
        .then((res) => {
          setServices(res.data.results || res.data);
        })
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [applicationId]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8 space-y-8">
      <h1 className="text-3xl font-bold">Services</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services.map((service) => (
          <Card key={service.id} className="group overflow-hidden">
            <div className="aspect-video w-full bg-muted relative">
                 {service.image_url ? (
                    <img src={service.image_url} alt={service.name} className="object-cover w-full h-full group-hover:scale-105 transition-transform" />
                 ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">No Image</div>
                 )}
            </div>
            <CardHeader>
              <CardTitle>{service.name}</CardTitle>
              <CardDescription className="line-clamp-2">
                {service.description}
              </CardDescription>
            </CardHeader>
            <CardFooter className="flex justify-between items-center">
              <div className="flex flex-col">
                {service.discounted_price && service.discounted_price !== service.price ? (
                    <>
                        <span className="text-sm text-muted-foreground line-through">
                            {Number(service.price).toLocaleString()} Toman
                        </span>
                        <span className="font-bold text-primary">
                            {Number(service.discounted_price).toLocaleString()} Toman
                        </span>
                    </>
                ) : (
                    <span className="font-bold">
                        {Number(service.price).toLocaleString()} Toman
                    </span>
                )}
              </div>
              <Button asChild>
                  <Link href={`/applications/${applicationId}/services/${service.id}`}>Buy Now</Link>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
