import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { Result, Status, Test } from "../types"
import { Simulation } from "../config/app"

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

export function getSimulationLabel(simulation: Simulation): string {
  switch (simulation) {
    case Simulation.ConsumeRLP:
      return "rlp";
    case Simulation.ConsumeEngine:
      return "eng";
    default:
      return simulation;
  }
}

export function getVariantCountsForSimulation(test: Test, clientId: string, simulation: Simulation): { passed: number; total: number } {
  if (!test.variants || test.variants.length === 0) {
    // For tests without variants, return 0 (no test results available)
    return { passed: 0, total: 0 };
  }

  // For tests with variants, count how many variants pass/fail for this simulation
  const variantResults = test.variants.map(variant => {
    const result = variant.results[clientId]?.find(r => r.simulation === simulation);
    return result?.status;
  }).filter(status => status !== undefined);

  const passed = variantResults.filter(status => status === "pass").length;
  const total = variantResults.length;

  return { passed, total };
}

export function getClientOverallProgress(tests: Test[], clientId: string): { passed: number; total: number } {
  let totalPassed = 0;
  let totalTests = 0;

  tests.forEach(test => {
    if (!test.variants || test.variants.length === 0) {
      return;
    }

    // Count variants - a variant passes only if ALL simulations pass
    test.variants.forEach(variant => {
      const clientResults = variant.results[clientId] || [];

      if (clientResults.length === 0) {
        return;
      }

      totalTests += 1;

      // Check if all simulations for this variant passed
      const allSimulationsPassed = Object.values(Simulation).every(simulation => {
        const result = clientResults.find(r => r.simulation === simulation);
        return result?.status === "pass";
      });

      if (allSimulationsPassed) {
        totalPassed += 1;
      }
    });
  });

  return { passed: totalPassed, total: totalTests };
}
