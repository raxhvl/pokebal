import StatusIcon from "./StatusIcon";
import { Test, Client } from "../types";

interface MobileTestCardProps {
  test: Test;
  clients: Client[];
  testIndex: number;
  lastUpdated?: string;
}

export default function MobileTestCard({ test, clients, testIndex, lastUpdated }: MobileTestCardProps) {
  return (
    <div
      className="rounded-xl border border-white/30 dark:border-gray-500/40 bg-white/15 dark:bg-gray-900/20 backdrop-blur-xl shadow-xl p-4"
      style={{ animationDelay: `${testIndex * 50}ms` }}
    >
      <div className="mb-4">
        <div className="font-mono text-sm font-medium text-gray-800 dark:text-gray-100 mb-1">
          {test.id}
        </div>
        <div className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
          {test.description}
        </div>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {clients.map((client) => (
          <div
            key={`${test.id}-${client.id}`}
            className="flex flex-col items-center space-y-2 p-3 rounded-lg bg-white/10 dark:bg-gray-800/15 border border-white/20 dark:border-gray-500/30"
          >
            <span className="text-xs font-bold text-gray-800 dark:text-gray-100">
              {client.name}
            </span>
            <div className="flex justify-center">
              <StatusIcon status={test.results[client.id]} size="small" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}