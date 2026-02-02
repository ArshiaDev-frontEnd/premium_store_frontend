"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Loader2, ShoppingCart } from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/store/authStore";

// Define Request/Response Types locally or imported
interface ServiceField {
  field_name: string;
  field_type: "text" | "password" | "email" | "username";
  is_required: boolean;
  label: string;
}

interface Service {
  id: number;
  name: string;
  price: number;
  discounted_price: number | null;
  required_fields: ServiceField[];
}

interface ServiceFormProps {
  service: Service;
}

export function ServiceForm({ service }: ServiceFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  
  // 1. Dynamically build Zod schema
  const schemaMap: Record<string, z.ZodType<any>> = {};
  
  service.required_fields.forEach((field) => {
    let validator = z.string();
    if (field.is_required) {
      if (field.field_type === 'email') {
        validator = validator.email("Invalid email address"); // Narrowing
      } else {
        validator = validator.min(1, `${field.label || field.field_name} is required`);
      }
    } else {
       validator = validator.optional() as any;
    }
    schemaMap[field.field_name] = validator;
  });

  const dynamicSchema = z.object(schemaMap);
  type FormValues = z.infer<typeof dynamicSchema>;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(dynamicSchema),
  });

  const onSubmit = async (data: FormValues) => {
    setLoading(true);
    try {
      // 1. Create a Cart if not exists (usually this logic is complex, 
      // but here we just POST /carts/ then POST /carts/{id}/items/)
      // Or we can just store in local storage using Zustand if we want offline cart?
      // API says: POST /carts/ -> id. POST /carts/<id>/items/.
      
      // Let's implement a simple flow: check local storage for cartId.
      let cartId = localStorage.getItem("cartId");
      if (!cartId) {
          const cartRes = await api.post("/carts/");
          cartId = cartRes.data.id;
          localStorage.setItem("cartId", cartId!);
      }

      await api.post(`/carts/${cartId}/items/`, {
        service: service.id,
        quantity: 1,
        extra_data: data,
      });
      
      router.push("/cart"); // Redirect to cart
    } catch (err) {
      console.error("Failed to add to cart", err);
      // Handle cart expired (404) -> create new cart logic
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-lg mx-auto">
      <CardHeader>
        <CardTitle>Configure {service.name}</CardTitle>
        <CardDescription>
          Please provide the required details to activate your service.
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {service.required_fields.map((field) => (
            <div key={field.field_name} className="space-y-2">
              <label 
                htmlFor={field.field_name} 
                className="text-sm font-medium capitalize"
              >
                {field.label || field.field_name.replace(/_/g, " ")}
                {field.is_required && <span className="text-destructive ml-1">*</span>}
              </label>
              <Input
                id={field.field_name}
                type={field.field_type === 'password' ? 'password' : 'text'}
                placeholder={`Enter ${field.label || field.field_name}`}
                {...register(field.field_name)}
              />
              {errors[field.field_name] && (
                <p className="text-sm text-destructive">
                   {errors[field.field_name]?.message as string}
                </p>
              )}
            </div>
          ))}
          
          {service.required_fields.length === 0 && (
              <p className="text-sm text-muted-foreground italic">
                  No additional information required for this service.
              </p>
          )}

        </CardContent>
        <CardFooter>
          <Button type="submit" className="w-full" size="lg" disabled={loading}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ShoppingCart className="mr-2 h-4 w-4" />}
            Add to Cart - {service.discounted_price ? Number(service.discounted_price).toLocaleString() : Number(service.price).toLocaleString()} Toman
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
