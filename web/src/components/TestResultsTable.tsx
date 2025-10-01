import StatusIcon from "./StatusIcon";
import ClientLogo from "./ClientLogo";
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
    <div className="hidden lg:block overflow-x-auto w-full">
      <div className="rounded-2xl border border-white/30 dark:border-gray-500/40 bg-white/15 dark:bg-gray-900/20 backdrop-blur-xl shadow-2xl">
        <div className="overflow-x-auto rounded-2xl">
          <table className="w-full border-collapse min-w-full">
            <thead>
              <tr className="bg-white dark:bg-gray-800 border-b border-white/30 dark:border-gray-500/40">
                <th className="p-2 text-left font-mono text-sm">
                  <div className="flex items-center space-x-2 mb-1">
                    <div className="w-2 h-2 bg-lime-500 rounded-full animate-pulse shadow-sm"></div>
                    <span className="font-bold text-gray-800 dark:text-gray-100">
                      Test Cases ({totalExecutions}) 
                    </span>
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      [including variants]
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
                      {client.githubRepo ? (
                        <a
                          href={client.githubRepo}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block hover:opacity-80 transition-opacity"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <div className="bg-white/25 dark:bg-gray-800/35 backdrop-blur-md px-3 py-1 rounded-lg border border-white/40 dark:border-gray-500/50 shadow-lg">
                            <div className="flex flex-col items-center space-y-1">
                              <div className="flex items-center space-x-2">
                                <ClientLogo
                                  logo={client.logo}
                                  name={client.name}
                                  size="small"
                                />
                                <span className="font-bold text-gray-800 dark:text-gray-100">
                                  {client.name}
                                </span>
                              </div>
                              <div
                                className="text-xs text-gray-600 dark:text-gray-400 font-mono truncate w-full px-1"
                                title={client.version}
                              >
                                {client.version}
                              </div>
                            </div>
                          </div>
                        </a>
                      ) : (
                        <div className="bg-white/25 dark:bg-gray-800/35 backdrop-blur-md px-3 py-1 rounded-lg border border-white/40 dark:border-gray-500/50 shadow-lg">
                          <div className="flex flex-col items-center space-y-1">
                            <div className="flex items-center space-x-2">
                              <ClientLogo
                                logo={client.logo}
                                name={client.name}
                                size="small"
                              />
                              <span className="font-bold text-gray-800 dark:text-gray-100">
                                {client.name}
                              </span>
                            </div>
                            <div
                              className="text-xs text-gray-600 dark:text-gray-400 font-mono truncate w-full px-1"
                              title={client.version}
                            >
                              {client.version}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tests.map((test, testIndex) => (
                <tr
                  key={test.id}
                  className="group hover:bg-white/10 dark:hover:bg-gray-800/20 transition-all duration-300 border-b border-white/20 dark:border-gray-500/30 last:border-b-0 cursor-pointer"
                  style={{ animationDelay: `${testIndex * 50}ms` }}
                  onClick={() => onTestClick(test)}
                >
                  <td className="p-2 border-r border-white/25 dark:border-gray-500/35">
                    <div className="transform transition-all duration-300 group-hover:translate-x-1 relative">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-mono text-xs font-medium text-gray-800 dark:text-gray-100 mb-1">
                            {formatTestId(test.id)}
                            {test.variants && test.variants.length > 1 && (
                              <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                                ({test.variants.length} variants)
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
                        className="p-2 text-center border-l border-white/15 dark:border-gray-500/25 w-32 min-w-32 max-w-32"
                      >
                        <div className="flex flex-col items-center space-y-0.5">
                          {Object.values(Simulation).map((simulation) => {
                            const { passed, total } = getVariantCountsForSimulation(test, client.id, simulation);
                            const simulationLabel = getSimulationLabel(simulation);
                            const allPassed = total > 0 && passed === total;
                            const anyFailed = total > 0 && passed < total;

                            return (
                              <div
                                key={simulation}
                                className="flex items-center space-x-1 text-xs"
                              >
                                <span className={`${
                                  allPassed ? 'text-green-600 dark:text-green-400' :
                                  anyFailed ? 'text-red-600 dark:text-red-400' :
                                  'text-gray-500 dark:text-gray-400'
                                }`}>
                                  {allPassed ? '✓' : anyFailed ? '✗' : '—'}
                                </span>
                                <span className="font-mono text-gray-700 dark:text-gray-300">
                                  {simulationLabel}
                                </span>
                                {total > 0 && (
                                  <span className="font-mono text-gray-600 dark:text-gray-400">
                                    ({passed}/{total})
                                  </span>
                                )}
                              </div>
                            );
                          })}
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
