import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { Result, Status } from "../types"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

export function formatTestId(id: string): string {
  return id
    .replace(/^test_bal_/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
}

export function getCombinedTestStatus(results: Result[]): Status {
  if (results.length === 0) return "pending";

  const hasAnyFail = results.some(result => result.status === "fail");
  if (hasAnyFail) return "fail";

  const allPass = results.every(result => result.status === "pass");
  if (allPass) return "pass";

  return "pending";
}

export function getSimulationCounts(results: Result[]): { passed: number; total: number } {
  const total = results.length;
  const passed = results.filter(result => result.status === "pass").length;
  return { passed, total };
}
