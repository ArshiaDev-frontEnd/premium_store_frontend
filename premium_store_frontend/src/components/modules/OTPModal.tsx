"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/store/authStore";

const otpSchema = z.object({
  code: z.string().length(6, "Code must be 6 digits"),
});

type OtpFormValues = z.infer<typeof otpSchema>;

interface OTPModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function OTPModal({ isOpen, onOpenChange }: OTPModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setUser = useAuthStore((state) => state.setUser);
  
  const {
      register,
      handleSubmit,
      formState: { errors },
  } = useForm<OtpFormValues>({
      resolver: zodResolver(otpSchema),
  });

  const onSubmit = async (data: OtpFormValues) => {
    setLoading(true);
    setError(null);
    try {
      await api.post("/customers/verify-phone/", { code: data.code });
      // Update user state locally or refetch profile
      const userRes = await api.get("/customers/me/");
      setUser(userRes.data);
      onOpenChange(false);
    } catch (err) {
      setError("Invalid code. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Verify Phone Number</DialogTitle>
          <DialogDescription>
            Enter the 6-digit code sent to your phone.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            placeholder="123456"
            className="text-center text-lg tracking-widest"
            maxLength={6}
            {...register("code")}
          />
          {errors.code && (
              <p className="text-sm text-destructive text-center">
                  {errors.code.message}
              </p>
          )}
          {error && <p className="text-sm text-destructive text-center">{error}</p>}
          <DialogFooter>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Verify
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
