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

function hasVariantPassedAllSimulations(clientResults: Result[]): boolean {
  return Object.values(Simulation).every(simulation => {
    const result = clientResults.find(r => r.simulation === simulation);
    return result?.status === "pass";
  });
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
      // Count tests without variants in total, but they can't be "passed"
      totalTests += 1;
      return;
    }

    // Count variants - a variant passes only if ALL simulations pass
    test.variants.forEach(variant => {
      totalTests += 1;

      const clientResults = variant.results[clientId] || [];

      if (clientResults.length === 0) {
        return;
      }

      // Check if all simulations for this variant passed
      if (hasVariantPassedAllSimulations(clientResults)) {
        totalPassed += 1;
      }
    });
  });

  return { passed: totalPassed, total: totalTests };
}

export interface ClientStats {
  clientId: string;
  passed: number;
  failed: number;
  pending: number;
  total: number;
  passRate: number;
}

export interface OverallAdoptionStats {
  totalClients: number;
  totalTests: number;
  totalVariants: number;
  overallPassRate: number;
  clientStats: ClientStats[];
}

export function getOverallAdoptionStats(tests: any[], clients: any[]): OverallAdoptionStats {
  // Calculate total variants across all tests
  const totalVariants = tests.reduce((total, test) => {
    return total + (test.variants?.length || 0);
  }, 0);

  // Calculate per-client statistics
  const clientStats: ClientStats[] = clients.map(client => {
    let passed = 0;
    let failed = 0;
    let pending = 0;
    let total = 0;

    tests.forEach(test => {
      if (!test.variants || test.variants.length === 0) {
        total += 1;
        pending += 1;
        return;
      }

      test.variants.forEach((variant: any) => {
        total += 1;
        const clientResults = variant.results[client.id] || [];

        if (clientResults.length === 0) {
          pending += 1;
          return;
        }

        // Check if all simulations for this variant passed
        const allSimulationsPassed = hasVariantPassedAllSimulations(clientResults);
        const anySimulationFailed = clientResults.some((r: any) => r.status === "fail");

        if (allSimulationsPassed) {
          passed += 1;
        } else if (anySimulationFailed) {
          failed += 1;
        } else {
          pending += 1;
        }
      });
    });

    const passRate = total > 0 ? (passed / total) * 100 : 0;

    return {
      clientId: client.id,
      passed,
      failed,
      pending,
      total,
      passRate,
    };
  });

  // Calculate overall pass rate across all clients
  const totalPossibleTests = clientStats.reduce((sum, stat) => sum + stat.total, 0);
  const totalPassed = clientStats.reduce((sum, stat) => sum + stat.passed, 0);
  const overallPassRate = totalPossibleTests > 0 ? (totalPassed / totalPossibleTests) * 100 : 0;

  return {
    totalClients: clients.length,
    totalTests: tests.length,
    totalVariants,
    overallPassRate,
    clientStats,
  };
}

export function isTestFailing(test: Test, clients: { id: string }[]): boolean {
  // A test is failing if any client has any failing variant for any simulation
  return clients.some(client => {
    return Object.values(Simulation).some(simulation => {
      const { passed, total } = getVariantCountsForSimulation(test, client.id, simulation);
      return total > 0 && passed < total;
    });
  });
}
