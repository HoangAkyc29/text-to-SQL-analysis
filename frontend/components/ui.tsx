"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { X } from "lucide-react";
import * as React from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-medium transition-all outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-[var(--accent)] text-white shadow-lg shadow-indigo-500/20 hover:-translate-y-0.5 hover:bg-[var(--accent-strong)]",
        secondary: "border border-[var(--border)] bg-[var(--panel)] hover:bg-[var(--muted)]",
        ghost: "hover:bg-[var(--muted)]",
        danger: "bg-red-500/10 text-red-500 hover:bg-red-500/20",
      },
      size: { sm: "h-8 px-3", md: "h-10 px-4", lg: "h-12 px-5", icon: "size-10" },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

export function Button({ className, variant, size, asChild, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "button";
  return <Comp className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn("h-11 w-full rounded-xl border border-[var(--border)] bg-[var(--panel)] px-3 text-sm outline-none transition focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-500/15", className)} {...props} />;
}

export function Textarea({ className, ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn("w-full resize-none rounded-2xl border border-[var(--border)] bg-[var(--panel)] px-4 py-3 text-sm outline-none transition placeholder:text-[var(--subtle)] focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-500/15", className)} {...props} />;
}

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-2xl border border-[var(--border)] bg-[var(--panel)] shadow-sm", className)} {...props} />;
}

export function Badge({ className, tone = "neutral", ...props }: React.HTMLAttributes<HTMLSpanElement> & { tone?: "neutral" | "success" | "warning" | "danger" | "accent" }) {
  const tones = {
    neutral: "bg-[var(--muted)] text-[var(--subtle)]",
    success: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
    warning: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
    danger: "bg-red-500/10 text-red-600 dark:text-red-400",
    accent: "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400",
  };
  return <span className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold", tones[tone], className)} {...props} />;
}

export function Modal({ open, onOpenChange, title, description, children }: { open: boolean; onOpenChange: (open: boolean) => void; title: string; description?: string; children: React.ReactNode }) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-slate-950/55 backdrop-blur-sm data-[state=open]:animate-in" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 max-h-[85vh] w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-auto rounded-3xl border border-[var(--border)] bg-[var(--panel)] p-6 shadow-2xl outline-none">
          <div className="pr-10"><Dialog.Title className="text-xl font-semibold">{title}</Dialog.Title>{description && <Dialog.Description className="mt-1 text-sm text-[var(--subtle)]">{description}</Dialog.Description>}</div>
          <Dialog.Close asChild><Button className="absolute right-4 top-4" variant="ghost" size="icon" aria-label="Close"><X className="size-4" /></Button></Dialog.Close>
          <div className="mt-5">{children}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-lg bg-[var(--muted)]", className)} />;
}
