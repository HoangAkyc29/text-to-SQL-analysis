import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LoginPage from "@/app/login/page";

const replace = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace, refresh: vi.fn() }) }));

describe("LoginPage", () => {
  beforeEach(() => { vi.restoreAllMocks(); replace.mockReset(); });

  it("validates required credentials", async () => {
    render(<LoginPage />);
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));
    expect(await screen.findByText("Enter your username")).toBeInTheDocument();
    expect(screen.getByText("Enter your password")).toBeInTheDocument();
  });

  it("submits credentials to the same-origin BFF", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ user: { role: "analyst" } }), { status: 200 })));
    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: "analyst" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secret" } });
    fireEvent.click(screen.getByRole("button", { name: /^sign in/i }));
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/"));
    expect(fetch).toHaveBeenCalledWith("/api/auth/login", expect.objectContaining({ method: "POST", credentials: "same-origin" }));
    vi.unstubAllGlobals();
  });
});
