import StatusIcon from "./StatusIcon";
import ClientLogo from "./ClientLogo";
import ClientLogoWithProgress from "./ClientLogoWithProgress";
import { Test, Client } from "../types";
import {
  formatDate,
  formatTestId,
  getCombinedTestStatus,
  getSimulationCounts,
  getSimulationLabel,
  getVariantCountsForSimulation,
} from "../lib/utils";
import { Simulation } from "../config/app";
import { Eye } from "lucide-react";

interface TestResultsTableProps {
  tests: Test[];
  clients: Client[];
  lastUpdated: string;
  onTestClick: (test: Test) => void;
}

export default function TestResultsTable({
  tests,
  clients,
  lastUpdated,
  onTestClick,
}: TestResultsTableProps) {
  // Calculate total test executions (including variants)
  const totalExecutions = tests.reduce((total, test) => {
    return total + (test.variants?.length || 1);
  }, 0);
  return (
    <div className="w-full">
      {/* Scroll hint for mobile */}
      <div className="lg:hidden text-center text-xs text-gray-500 dark:text-gray-400 mb-2">
        ← Scroll to see all clients →
      </div>
      <div className="rounded-2xl border border-white/30 dark:border-gray-500/40 bg-white/15 dark:bg-gray-900/20 backdrop-blur-xl shadow-2xl">
        <div
          className="overflow-x-auto rounded-2xl overscroll-x-contain"
          style={{ WebkitOverflowScrolling: "touch" }}
        >
          <table className="w-full border-collapse min-w-[700px]">
            <thead>
              <tr className="bg-white dark:bg-gray-800 border-b border-white/30 dark:border-gray-500/40">
                <th className="p-2 text-left font-mono text-sm">
                  <div className="flex items-center space-x-2 mb-1">
                    <div className="w-2 h-2 bg-lime-500 rounded-full animate-pulse shadow-sm"></div>
                    <span className="font-bold text-gray-800 dark:text-gray-100">
                      Test Cases ({tests.length})
                    </span>
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      [{totalExecutions} total variants]
                    </span>
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Updated {formatDate(lastUpdated)}
                  </div>
                </th>
                {clients.map((client, index) => (
                  <th
                    key={client.id}
                    className="p-2 text-center font-mono text-sm group border-l border-white/20 dark:border-gray-500/30 w-40 min-w-40 max-w-40"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="transform transition-all duration-300 group-hover:scale-105">
                      <ClientLogoWithProgress client={client} tests={tests} />
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tests.map((test, testIndex) => (
                <tr
                  key={test.id}
                  className="group hover:bg-white/10 dark:hover:bg-gray-700/30 transition-all duration-300 border-b border-white/20 dark:border-gray-500/30 last:border-b-0 cursor-pointer"
                  style={{ animationDelay: `${testIndex * 50}ms` }}
                  onClick={() => onTestClick(test)}
                >
                  <td className="px-3 py-2 border-r border-white/25 dark:border-gray-500/35">
                    <div className="transform transition-all duration-300 group-hover:translate-x-1 relative">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-mono text-xs font-medium text-gray-800 dark:text-gray-100 mb-1">
                            {formatTestId(test.id)}
                            {test.variants && (
                              <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                                ({test.variants.length}{" "}
                                {test.variants.length === 1
                                  ? "variant"
                                  : "variants"}
                                )
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-600 dark:text-gray-300 leading-tight">
                            {test.description}
                          </div>
                        </div>
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 ml-2">
                          <Eye className="w-4 h-4 text-lime-500" />
                        </div>
                      </div>
                    </div>
                  </td>
                  {clients.map((client) => {
                    return (
                      <td
                        key={`${test.id}-${client.id}`}
                        className="px-2 py-2 text-center border-l border-white/15 dark:border-gray-500/25 w-28 min-w-28 max-w-28"
                      >
                        <div className="flex flex-col items-center space-y-2">
                          {/* Overall status icon */}
                          <div className="flex items-center justify-center">
                            {(() => {
                              const rlpCounts = getVariantCountsForSimulation(
                                test,
                                client.id,
                                Simulation.ConsumeRLP
                              );
                              const engineCounts =
                                getVariantCountsForSimulation(
                                  test,
                                  client.id,
                                  Simulation.ConsumeEngine
                                );

                              const rlpAllPassed =
                                rlpCounts.total > 0 &&
                                rlpCounts.passed === rlpCounts.total;
                              const rlpAnyFailed =
                                rlpCounts.total > 0 &&
                                rlpCounts.passed < rlpCounts.total;

                              const engineAllPassed =
                                engineCounts.total > 0 &&
                                engineCounts.passed === engineCounts.total;
                              const engineAnyFailed =
                                engineCounts.total > 0 &&
                                engineCounts.passed < engineCounts.total;

                              const bothPass = rlpAllPassed && engineAllPassed;
                              const anyFail = rlpAnyFailed || engineAnyFailed;

                              let overallStatus: "pass" | "fail" | "pending";
                              if (bothPass) {
                                overallStatus = "pass";
                              } else if (anyFail) {
                                overallStatus = "fail";
                              } else {
                                overallStatus = "pending";
                              }

                              return (
                                <StatusIcon
                                  status={overallStatus}
                                  size="small"
                                />
                              );
                            })()}
                          </div>

                          {/* Counts */}
                          <div className="flex flex-col items-center space-y-1">
                            {Object.values(Simulation).map((simulation) => {
                              const { passed, total } =
                                getVariantCountsForSimulation(
                                  test,
                                  client.id,
                                  simulation
                                );
                              const simulationLabel =
                                getSimulationLabel(simulation);
                              const isAllPassed = total > 0 && passed === total;
                              const hasFailed = total > 0 && passed < total;

                              return (
                                <div
                                  key={simulation}
                                  className={`text-xs font-mono p-1 rounded ${
                                    isAllPassed
                                      ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                                      : hasFailed
                                      ? "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300"
                                      : "bg-gray-100 dark:bg-gray-800/50 text-gray-600 dark:text-gray-400"
                                  }`}
                                  title={`${simulationLabel}: ${passed}/${total} passed`}
                                >
                                  <span>{simulationLabel.toLowerCase()}</span>{" "}
                                  <span className="font-bold">
                                    {passed}/{total}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
