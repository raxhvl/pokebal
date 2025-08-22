import DotGrid from "../components/DotGrid";
import TestResultsTable from "../components/TestResultsTable";
import MobileTestCard from "../components/MobileTestCard";
import Legend from "../components/Legend";
import clientsData from "../data/clients.json";

export default function Home() {
  const { tests, clients } = clientsData;

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
          <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Poké<span className="text-lime-500">BAL</span>
          </h1>
          <p className="text-gray-600 dark:text-gray-400 italic">
            &gt; gotta access 'em all!
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-4">
            EIP-7928 Block Access Lists adoption tracker
          </p>
        </div>

        <TestResultsTable tests={tests} clients={clients} />

        <div className="lg:hidden space-y-4">
          {tests.map((test, testIndex) => (
            <MobileTestCard
              key={test.id}
              test={test}
              clients={clients}
              testIndex={testIndex}
            />
          ))}
        </div>

        <Legend />
      </div>
    </div>
  );
}
