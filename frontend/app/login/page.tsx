"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { ArrowRight, Bot, CheckCircle2, Eye, EyeOff, LockKeyhole, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button, Input } from "@/components/ui";
import { api } from "@/lib/utils";

const schema = z.object({
  username: z.string().trim().min(1, "Enter your username"),
  password: z.string().min(1, "Enter your password"),
});
type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const { register, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const submit = handleSubmit(async (values) => {
    try {
      await api("/api/auth/login", { method: "POST", body: JSON.stringify(values) });
      router.replace("/");
      router.refresh();
    } catch (error) {
      setError("root", { message: error instanceof Error ? error.message.replaceAll("_", " ") : "Unable to sign in" });
    }
  });

  return (
    <main className="grid min-h-screen lg:grid-cols-[1.08fr_.92fr]">
      <section className="relative hidden overflow-hidden border-r border-[var(--border)] bg-[#0b1020] p-12 text-white lg:flex lg:flex-col">
        <div className="grid-bg absolute inset-0 opacity-[.06]" />
        <div className="absolute -left-32 top-1/4 size-96 rounded-full bg-indigo-500/25 blur-3xl" />
        <div className="relative flex items-center gap-3 text-lg font-semibold"><span className="grid size-10 place-items-center rounded-xl bg-indigo-500"><Bot /></span>Axiom Agent</div>
        <motion.div className="relative my-auto max-w-xl" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}>
          <span className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-indigo-200"><Sparkles className="size-4" />Human-guided intelligence</span>
          <h1 className="text-5xl font-semibold leading-[1.08] tracking-tight">Complex analysis,<br /><span className="text-indigo-400">made conversational.</span></h1>
          <p className="mt-6 max-w-lg text-lg leading-8 text-slate-300">Collaborate with specialized agents, review every decision, and turn trustworthy data into action.</p>
          <div className="mt-10 grid gap-4 text-sm text-slate-300">
            {["Transparent multi-agent workflows", "Secure, permission-aware analysis", "Reviewable results and artifacts"].map((item) => <div className="flex items-center gap-3" key={item}><CheckCircle2 className="size-5 text-emerald-400" />{item}</div>)}
          </div>
        </motion.div>
        <p className="relative text-xs text-slate-500">Enterprise analysis workspace · Secure by default</p>
      </section>

      <section className="flex items-center justify-center p-6 sm:p-12">
        <motion.div className="w-full max-w-md" initial={{ opacity: 0, scale: .98 }} animate={{ opacity: 1, scale: 1 }}>
          <div className="mb-10 flex items-center gap-3 lg:hidden"><span className="grid size-10 place-items-center rounded-xl bg-[var(--accent)] text-white"><Bot /></span><span className="font-semibold">Axiom Agent</span></div>
          <div className="mb-8">
            <div className="mb-5 grid size-12 place-items-center rounded-2xl bg-indigo-500/10 text-indigo-500"><LockKeyhole /></div>
            <h2 className="text-3xl font-semibold tracking-tight">Welcome back</h2>
            <p className="mt-2 text-[var(--subtle)]">Sign in to continue to your analysis workspace.</p>
          </div>
          <form className="space-y-5" onSubmit={submit}>
            <label className="block text-sm font-medium">Username<Input className="mt-2" autoComplete="username" placeholder="you@company.com" {...register("username")} />{errors.username && <span className="mt-1 block text-xs text-red-500">{errors.username.message}</span>}</label>
            <label className="block text-sm font-medium">Password<div className="relative mt-2"><Input className="pr-12" autoComplete="current-password" type={showPassword ? "text" : "password"} placeholder="••••••••" {...register("password")} /><button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--subtle)]" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}</button></div>{errors.password && <span className="mt-1 block text-xs text-red-500">{errors.password.message}</span>}</label>
            {errors.root && <div role="alert" className="rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-600">{errors.root.message}</div>}
            <Button className="w-full" size="lg" disabled={isSubmitting}>{isSubmitting ? "Signing in…" : "Sign in"}<ArrowRight className="size-4" /></Button>
          </form>
          <p className="mt-8 text-center text-xs leading-5 text-[var(--subtle)]">Credentials are sent only to the same-origin secure gateway. Sessions are stored in HttpOnly cookies.</p>
        </motion.div>
      </section>
    </main>
  );
}
