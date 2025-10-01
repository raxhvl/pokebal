import StatusIcon from "./StatusIcon";
import { Test, Client } from "../types";
import { Eye } from "lucide-react";
import { formatTestId, getCombinedTestStatus, getSimulationCounts, getSimulationLabel, getVariantCountsForSimulation } from "../lib/utils";
import { Simulation } from "../config/app";

interface MobileTestCardProps {
  test: Test;
  clients: Client[];
  testIndex: number;
  lastUpdated?: string;
  onTestClick: (test: Test) => void;
}

export default function MobileTestCard({ test, clients, testIndex, lastUpdated, onTestClick }: MobileTestCardProps) {
  return (
    <div
      className="group rounded-xl border border-white/30 dark:border-gray-500/40 bg-white/15 dark:bg-gray-900/20 backdrop-blur-xl shadow-xl p-4 cursor-pointer transition-all duration-300 hover:bg-white/20 dark:hover:bg-gray-900/30 hover:border-lime-500/30"
      style={{ animationDelay: `${testIndex * 50}ms` }}
      onClick={() => onTestClick(test)}
    >
      <div className="mb-4 relative">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="font-mono text-sm font-medium text-gray-800 dark:text-gray-100 mb-1">
              {formatTestId(test.id)}
              {test.variants && test.variants.length > 1 && (
                <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                  ({test.variants.length} variants)
                </span>
              )}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
              {test.description}
            </div>
          </div>
          <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 ml-2">
            <Eye className="w-4 h-4 text-lime-500" />
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {clients.map((client) => {
          return (
            <div
              key={`${test.id}-${client.id}`}
              className="flex flex-col items-center space-y-2 p-3 rounded-lg bg-white/10 dark:bg-gray-800/15 border border-white/20 dark:border-gray-500/30"
            >
              <span className="text-xs font-bold text-gray-800 dark:text-gray-100">
                {client.name}
              </span>
              <div className="flex flex-col items-center space-y-1">
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
            </div>
          );
        })}
      </div>
    </div>
  );
}