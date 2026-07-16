import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import ChatInterface from "../components/ChatInterface";
import "../i18n";

vi.mock("../services/api", () => ({
  sendChat: vi.fn().mockResolvedValue({
    reply: "Gate A is on the north side of the stadium.",
    suggested_actions: ["Find restroom", "Transport options"],
    alert: null,
  }),
}));

describe("ChatInterface", () => {
  it("renders the welcome message on load", () => {
    render(<ChatInterface persona="fan" language="en" onAlert={vi.fn()} highContrast={false} />);
    expect(screen.getByRole("log")).toBeInTheDocument();
  });
  
  it("renders the send button", () => {
    render(<ChatInterface persona="fan" language="en" onAlert={vi.fn()} highContrast={false} />);
    expect(screen.getByLabelText(/send message/i)).toBeInTheDocument();
  });
  
  it("send button is disabled when input is empty", () => {
    render(<ChatInterface persona="fan" language="en" onAlert={vi.fn()} highContrast={false} />);
    const btn = screen.getByLabelText(/send message/i);
    expect(btn).toBeDisabled();
  });
});
