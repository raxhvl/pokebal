import DotGrid from "../components/DotGrid";
import TestResultsTable from "../components/TestResultsTable";
import MobileTestCard from "../components/MobileTestCard";
import Legend from "../components/Legend";
import { TestResults, Clients } from "../types";
import testResultsData from "../data/test_results.json";
import clientsData from "../data/clients.json";
import { formatDate } from "../utils/dateFormat";

export default function Home() {
  const { tests, lastUpdated } = testResultsData as TestResults;
  const clients = clientsData as Clients;

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 font-mono relative">
      <div className="fixed inset-0 z-0">
        <DotGrid
          dotSize={5}
          gap={18}
          baseColor="#271E37"
          activeColor="#84cc16"
          proximity={120}
          shockRadius={250}
          shockStrength={5}
          resistance={750}
          returnDuration={1.5}
          className="w-full h-full"
        />
      </div>
      {/* Content overlay */}
      <div className="relative z-10 max-w-6xl mx-auto p-8">
        {/* Simple header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-1">
            Poké<span className="text-lime-500">BAL</span>
          </h1>
          <p className="text-gray-500 dark:text-gray-600 text-sm italic">
            &gt; gotta access 'em all!
          </p>
          <p className="text-base text-gray-700 dark:text-gray-300 mt-4">
            <a
              href="https://eips.ethereum.org/EIPS/eip-7928"
              className="text-lime-500 hover:text-lime-400 underline underline-offset-2"
            >
              EIP-7928 Block Access Lists
            </a>{" "}
            adoption tracker
          </p>
        </div>

        <TestResultsTable
          tests={tests}
          clients={clients}
          lastUpdated={lastUpdated}
        />

        <div className="lg:hidden">
          <div className="mb-4 text-center">
            <div className="flex items-center justify-center space-x-2 mb-1">
              <div className="w-2 h-2 bg-lime-500 rounded-full animate-pulse shadow-sm"></div>
              <span className="font-bold text-gray-800 dark:text-gray-100 font-mono text-sm">
                Test Cases
              </span>
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">
              Updated {formatDate(lastUpdated)}
            </div>
          </div>
          <div className="space-y-4">
            {tests.map((test, testIndex) => (
              <MobileTestCard
                key={test.id}
                test={test}
                clients={clients}
                testIndex={testIndex}
              />
            ))}
          </div>
        </div>

        <Legend />
      </div>
    </div>
  );
}
