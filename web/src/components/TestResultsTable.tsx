import StatusIcon from "./StatusIcon";
import ClientLogo from "./ClientLogo";
import { Test, Client } from "../types";

interface TestResultsTableProps {
  tests: Test[];
  clients: Client[];
}

export default function TestResultsTable({ tests, clients }: TestResultsTableProps) {
  return (
    <div className="hidden lg:block overflow-x-auto">
      <div className="rounded-2xl border border-white/30 dark:border-gray-500/40 bg-white/15 dark:bg-gray-900/20 backdrop-blur-xl shadow-2xl">
        <div className="overflow-hidden rounded-2xl">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-white/10 dark:bg-gray-800/15 border-b border-white/30 dark:border-gray-500/40">
                <th className="p-4 text-left font-mono text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-lime-500 rounded-full animate-pulse shadow-sm"></div>
                    <span className="font-bold text-gray-800 dark:text-gray-100">Test Suite</span>
                  </div>
                </th>
                {clients.map((client, index) => (
                  <th
                    key={client.id}
                    className="p-4 text-center font-mono text-sm group border-l border-white/20 dark:border-gray-500/30"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="transform transition-all duration-300 group-hover:scale-105">
                      <div className="bg-white/25 dark:bg-gray-800/35 backdrop-blur-md px-3 py-1 rounded-lg border border-white/40 dark:border-gray-500/50 shadow-lg">
                        <div className="flex items-center space-x-2">
                          <ClientLogo logo={client.logo} name={client.name} size="small" />
                          <span className="font-bold text-gray-800 dark:text-gray-100">{client.name}</span>
                        </div>
                      </div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tests.map((test, testIndex) => (
                <tr
                  key={test.id}
                  className="group hover:bg-white/5 dark:hover:bg-gray-800/10 transition-all duration-300 border-b border-white/20 dark:border-gray-500/30 last:border-b-0"
                  style={{ animationDelay: `${testIndex * 50}ms` }}
                >
                  <td className="p-4 border-r border-white/25 dark:border-gray-500/35">
                    <div className="transform transition-all duration-300 group-hover:translate-x-1">
                      <div className="font-mono text-sm font-medium text-gray-800 dark:text-gray-100 mb-1">
                        {test.name}
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                        {test.description}
                      </div>
                    </div>
                  </td>
                  {clients.map((client) => (
                    <td
                      key={`${test.id}-${client.id}`}
                      className="p-4 text-center border-l border-white/15 dark:border-gray-500/25"
                    >
                      <div className="flex justify-center">
                        <StatusIcon status={client.testResults[test.id]} size="large" />
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}