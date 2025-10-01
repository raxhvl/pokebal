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
      className={`group rounded-xl border border-white/30 dark:border-gray-500/40 backdrop-blur-xl shadow-xl p-4 cursor-pointer transition-all duration-300 hover:border-lime-500/30 ${
        testIndex % 2 === 0
          ? 'bg-white/20 dark:bg-gray-800/40 hover:bg-white/25 dark:hover:bg-gray-800/50'
          : 'bg-white/15 dark:bg-gray-900/30 hover:bg-white/20 dark:hover:bg-gray-900/40'
      }`}
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
              <div className="flex flex-col items-center space-y-3">
                {/* Overall status icon */}
                <div className="flex items-center justify-center">
                  {(() => {
                    const rlpCounts = getVariantCountsForSimulation(test, client.id, Simulation.ConsumeRLP);
                    const engineCounts = getVariantCountsForSimulation(test, client.id, Simulation.ConsumeEngine);

                    const rlpAllPassed = rlpCounts.total > 0 && rlpCounts.passed === rlpCounts.total;
                    const rlpAnyFailed = rlpCounts.total > 0 && rlpCounts.passed < rlpCounts.total;
                    const rlpPending = rlpCounts.total === 0;

                    const engineAllPassed = engineCounts.total > 0 && engineCounts.passed === engineCounts.total;
                    const engineAnyFailed = engineCounts.total > 0 && engineCounts.passed < engineCounts.total;
                    const enginePending = engineCounts.total === 0;

                    const bothPass = rlpAllPassed && engineAllPassed;
                    const anyFail = rlpAnyFailed || engineAnyFailed;
                    const bothPending = rlpPending && enginePending;

                    let overallStatus: 'pass' | 'fail' | 'pending';
                    if (bothPass) {
                      overallStatus = 'pass';
                    } else if (anyFail) {
                      overallStatus = 'fail';
                    } else {
                      overallStatus = 'pending';
                    }

                    return (
                      <StatusIcon
                        status={overallStatus}
                        size="medium"
                      />
                    );
                  })()}
                </div>

                {/* Counts */}
                <div className="flex flex-col items-center space-y-1">
                  {Object.values(Simulation).map((simulation) => {
                    const { passed, total } = getVariantCountsForSimulation(test, client.id, simulation);
                    const simulationLabel = getSimulationLabel(simulation);

                    return (
                      <div
                        key={simulation}
                        className="text-xs font-mono text-gray-600 dark:text-gray-400"
                        title={`${simulationLabel}: ${passed}/${total} passed`}
                      >
                        {simulationLabel.toLowerCase()} {passed}/{total}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}