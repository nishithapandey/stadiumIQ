import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import PersonaSelector from "../components/PersonaSelector";
import "../i18n";

describe("PersonaSelector", () => {
  it("renders all four persona buttons", () => {
    render(<PersonaSelector persona="fan" setPersona={vi.fn()} highContrast={false} />);
    expect(screen.getByText(/fan/i)).toBeInTheDocument();
    expect(screen.getByText(/staff/i)).toBeInTheDocument();
    expect(screen.getByText(/volunteer/i)).toBeInTheDocument();
    expect(screen.getByText(/organizer/i)).toBeInTheDocument();
  });
  
  it("calls setPersona when a button is clicked", () => {
    const mockSet = vi.fn();
    render(<PersonaSelector persona="fan" setPersona={mockSet} highContrast={false} />);
    fireEvent.click(screen.getByText(/staff/i));
    expect(mockSet).toHaveBeenCalledWith("staff");
  });
  
  it("marks the active persona as pressed", () => {
    render(<PersonaSelector persona="volunteer" setPersona={vi.fn()} highContrast={false} />);
    const volunteerBtn = screen.getByText(/volunteer/i).closest("button");
    expect(volunteerBtn).toHaveAttribute("aria-pressed", "true");
  });
});
