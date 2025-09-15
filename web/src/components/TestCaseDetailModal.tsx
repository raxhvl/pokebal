import { Test, Client } from "../types";
import { Simulation } from "../config/app";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import StatusIcon from "./StatusIcon";
import ClientLogo from "./ClientLogo";
import { formatTestId, getCombinedTestStatus } from "../lib/utils";

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
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-hidden bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border border-white/30 dark:border-gray-500/40 p-0">
        <div className="overflow-y-auto max-h-[85vh]">
          <DialogHeader className="px-6 pt-6 pb-4 border-b border-white/20 dark:border-gray-500/20">
            <div className="flex items-center justify-between">
              <div>
                <DialogTitle className="text-xl font-mono text-gray-800 dark:text-gray-100 mb-1">
                  {formatTestId(test.id)}
                </DialogTitle>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    test.status === 'completed' 
                      ? 'bg-lime-100 text-lime-800 dark:bg-lime-900/30 dark:text-lime-400'
                      : 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
                  }`}>
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

            {/* Client Results - Showing Multiple Simulations */}
            <div>
              <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-3 uppercase tracking-wide">
                Implementation Status
              </h4>
              <div className="space-y-3">
                {clients.map((client) => {
                  const clientResults = test.results[client.id] || [];
                  const combinedStatus = getCombinedTestStatus(clientResults);

                  return (
                    <div
                      key={client.id}
                      className="p-3 bg-white/15 dark:bg-gray-800/15 rounded border border-white/20 dark:border-gray-500/20"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <ClientLogo
                            logo={client.logo}
                            name={client.name}
                            size="small"
                          />
                          <span className="font-medium text-sm text-gray-800 dark:text-gray-100">
                            {client.name}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-gray-600 dark:text-gray-400">
                            Overall:
                          </span>
                          <div className="scale-75">
                            <StatusIcon
                              status={combinedStatus}
                              size="small"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Individual Simulation Results */}
                      <div className="space-y-1">
                        {Object.values(Simulation).map((simulationType) => {
                          const simulationResult = clientResults.find(r => r.simulation === simulationType);
                          const status = simulationResult?.status || "pending";

                          return (
                            <div
                              key={simulationType}
                              className="flex items-center justify-between py-1 px-2 bg-white/10 dark:bg-gray-700/10 rounded text-xs"
                            >
                              <span className="text-gray-700 dark:text-gray-300 font-mono">
                                {simulationType}
                              </span>
                              <div className="scale-75">
                                <StatusIcon
                                  status={status}
                                  size="small"
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}