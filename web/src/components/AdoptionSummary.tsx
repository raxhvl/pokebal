import { Test, Client } from "../types";
import { getOverallAdoptionStats } from "../lib/utils";
import { config } from "../config/app";
import CountUp from "./ui/CountUp";

interface AdoptionSummaryProps {
  tests: Test[];
  clients: Client[];
}

export default function AdoptionSummary({
  tests,
  clients,
}: AdoptionSummaryProps) {
  // Filter clients to only include those with known versions (active implementations)
  const activeClients = clients.filter((c) => c.version !== "unknown");

  // Get stats only from active clients
  const stats = getOverallAdoptionStats(tests, activeClients);

  // Extract version from config
  const testVersion = config.hive.buildArgs.fixtures.split("@")[1] || "unknown";

  return (
    <div className="rounded-2xl border border-white/30 dark:border-gray-500/40 bg-white/5 dark:bg-gray-900/10 backdrop-blur-xl shadow-2xl p-8">
      {/* Title Section */}
      <div className="text-center mb-6">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-1">
          Poké<span className="text-lime-500">BAL</span>
        </h1>
        <p className="text-gray-500 dark:text-gray-600 text-sm italic mb-4">
          &gt; gotta access 'em all!
        </p>
        <p className="text-base text-gray-700 dark:text-gray-300">
          <a
            href="https://eips.ethereum.org/EIPS/eip-7928"
            className="text-lime-500 hover:text-lime-400 underline underline-offset-2"
          >
            EIP-7928 Block Access Lists
          </a>{" "}
          adoption tracker
        </p>
      </div>

      {/* Summary Statement */}
      <div className="text-center pt-6 border-t border-white/20 dark:border-gray-500/30">
        <p className="text-base text-gray-700 dark:text-gray-300 leading-relaxed">
          BAL is now adopted by{" "}
          <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-lime-500/15 border border-lime-500/30 text-lime-600 dark:text-lime-400 font-bold min-w-[2ch]">
            <CountUp
              from={0}
              to={activeClients.length}
              className="font-bold text-lime-600 dark:text-lime-400"
              duration={2}
              delay={0.2}
            />
          </span> of{" "}
          <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-lime-500/15 border border-lime-500/30 text-lime-600 dark:text-lime-400 font-bold min-w-[2ch]">
            <CountUp
              from={0}
              to={clients.length}
              className="font-bold text-lime-600 dark:text-lime-400"
              duration={2}
              delay={0.4}
            />
          </span> clients. For test
          version <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-lime-500/15 border border-lime-500/30 text-lime-600 dark:text-lime-400 font-bold">{testVersion}</span>,
          the average pass rate is{" "}
          <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-lime-500/15 border border-lime-500/30 text-lime-600 dark:text-lime-400 font-bold min-w-[3ch]">
            <CountUp
              from={0}
              to={Math.round(stats.overallPassRate)}
              className="font-bold text-lime-600 dark:text-lime-400"
              duration={2}
              delay={0.6}
            />%
          </span>.
        </p>
      </div>
    </div>
  );
}
