import { Test, Client } from "../types";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import StatusIcon from "./StatusIcon";
import ClientLogo from "./ClientLogo";

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
                  {test.id}
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

            {/* Client Results - Horizontal Layout */}
            <div>
              <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-3 uppercase tracking-wide">
                Implementation Status
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {clients.map((client) => (
                  <div
                    key={client.id}
                    className="flex items-center justify-between p-2 bg-white/15 dark:bg-gray-800/15 rounded border border-white/20 dark:border-gray-500/20"
                  >
                    <div className="flex items-center space-x-2 min-w-0">
                      <ClientLogo
                        logo={client.logo}
                        name={client.name}
                        size="small"
                      />
                      <span className="font-medium text-xs text-gray-800 dark:text-gray-100 truncate">
                        {client.name}
                      </span>
                    </div>
                    <div 
                      className="relative group"
                      title={test.results[client.id].charAt(0).toUpperCase() + test.results[client.id].slice(1)}
                    >
                      <div className="scale-75">
                        <StatusIcon
                          status={test.results[client.id]}
                          size="small"
                        />
                      </div>
                      {/* Tooltip */}
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 px-2 py-1 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                        {test.results[client.id].charAt(0).toUpperCase() + test.results[client.id].slice(1)}
                        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-2 border-r-2 border-t-2 border-l-transparent border-r-transparent border-t-gray-900 dark:border-t-gray-100"></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}