import { Test, Client } from "../types";
import { Simulation } from "../config/app";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import StatusIcon from "./StatusIcon";
import ClientLogo from "./ClientLogo";
import { formatTestId } from "../lib/utils";

interface TestCaseDetailModalProps {
  test: Test | null;
  clients: Client[];
  isOpen: boolean;
  onClose: () => void;
}

export default function TestCaseDetailModal({
  test,
  clients,
  isOpen,
  onClose,
}: TestCaseDetailModalProps) {
  if (!test) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-[90vw] lg:min-w-2xl overflow-hidden bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border border-white/30 dark:border-gray-500/40 p-0">
        <div className="overflow-y-auto max-h-[80vh]">
          <DialogHeader className="px-6 pt-6 pb-4 border-b border-white/20 dark:border-gray-500/20">
            <div className="flex items-center justify-between">
              <div>
                <DialogTitle className="text-xl font-mono text-gray-800 dark:text-gray-100 mb-1">
                  {formatTestId(test.id)}
                </DialogTitle>
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      test.status === "completed"
                        ? "bg-lime-100 text-lime-800 dark:bg-lime-900/30 dark:text-lime-400"
                        : "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400"
                    }`}
                  >
                    {test.status.charAt(0).toUpperCase() + test.status.slice(1)}
                  </span>
                </div>
              </div>
            </div>
          </DialogHeader>

          <div className="px-6 py-4 space-y-4">
            {/* Description */}
            <div>
              <p className="text-gray-800 dark:text-gray-100 text-sm leading-relaxed">
                {test.description}
              </p>
            </div>

            {/* Setup & Expectation in compact layout */}
            <div className="grid gap-4">
              <div className="bg-white/20 dark:bg-gray-800/20 rounded-lg p-3 border border-white/30 dark:border-gray-500/20">
                <h4 className="text-xs font-semibold text-lime-600 dark:text-lime-400 mb-2 uppercase tracking-wide">
                  Setup
                </h4>
                <p className="text-gray-700 dark:text-gray-300 text-xs font-mono leading-relaxed">
                  {test.setup}
                </p>
              </div>

              <div className="bg-white/20 dark:bg-gray-800/20 rounded-lg p-3 border border-white/30 dark:border-gray-500/20">
                <h4 className="text-xs font-semibold text-lime-600 dark:text-lime-400 mb-2 uppercase tracking-wide">
                  Expected Result
                </h4>
                <p className="text-gray-700 dark:text-gray-300 text-xs font-mono leading-relaxed">
                  {test.expectation}
                </p>
              </div>
            </div>

            {/* Test Results Table */}
            {test.variants && (
              <div>
                <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-3 uppercase tracking-wide">
                  Test Variants ({test.variants.length})
                </h4>
                <div className="bg-white/10 dark:bg-gray-800/10 rounded-lg border border-white/20 dark:border-gray-500/20 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="bg-white/20 dark:bg-gray-800/20 border-b border-white/20 dark:border-gray-500/20">
                          <th className="text-left p-3 font-medium text-gray-700 dark:text-gray-300">
                            Parameters
                          </th>
                          {clients.map((client) => (
                            <th
                              key={client.id}
                              className="text-center p-3 font-medium text-gray-700 dark:text-gray-300 border-l border-white/20 dark:border-gray-500/20"
                            >
                              {client.name}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {test.variants.map((variant, index) => (
                          <tr
                            key={index}
                            className={`${
                              index % 2 === 0
                                ? "bg-white/5 dark:bg-gray-800/5"
                                : ""
                            } border-b border-white/10 dark:border-gray-500/10 last:border-b-0`}
                          >
                            <td className="p-3">
                              {variant.parameters && variant.parameters.length > 0 ? (
                                <div className="flex flex-wrap gap-1">
                                  {variant.parameters.map((param, paramIndex) => (
                                    <span
                                      key={paramIndex}
                                      className="px-2 py-0.5 bg-gray-200/30 dark:bg-gray-700/30 rounded text-gray-700 dark:text-gray-300 font-mono text-xs"
                                    >
                                      {param}
                                    </span>
                                  ))}
                                </div>
                              ) : (
                                <span className="text-gray-500 dark:text-gray-400 italic">
                                  standalone
                                </span>
                              )}
                            </td>
                            {clients.map((client) => {
                              const clientResults =
                                variant.results[client.id] || [];

                              return (
                                <td
                                  key={`${index}-${client.id}`}
                                  className="p-3 text-center border-l border-white/10 dark:border-gray-500/10"
                                >
                                  <div className="flex flex-col items-center space-y-1">
                                    {Object.values(Simulation).map(
                                      (simulationType) => {
                                        const simulationResult =
                                          clientResults.find(
                                            (r) =>
                                              r.simulation === simulationType
                                          );
                                        const status =
                                          simulationResult?.status || "pending";

                                        const getStatusStyles = () => {
                                          switch (status) {
                                            case "pass":
                                              return "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300";
                                            case "fail":
                                              return "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300";
                                            case "pending":
                                            default:
                                              return "bg-gray-100 dark:bg-gray-800/50 text-gray-600 dark:text-gray-400";
                                          }
                                        };

                                        const simulationLabel = simulationType === Simulation.ConsumeRLP ? "rlp" : "engine";

                                        return (
                                          <div
                                            key={simulationType}
                                            className={`inline-flex items-center gap-1 text-xs font-mono p-1 rounded ${getStatusStyles()}`}
                                            title={`${simulationType}: ${status}`}
                                          >
                                            <div className="scale-75">
                                              <StatusIcon
                                                status={status}
                                                size="small"
                                              />
                                            </div>
                                            <span>{simulationLabel}</span>
                                          </div>
                                        );
                                      }
                                    )}
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
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
