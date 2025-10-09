"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import DotGrid from "../components/DotGrid";
import TestResultsTable from "../components/TestResultsTable";
import TestCaseDetailModal from "../components/TestCaseDetailModal";
import Legend from "../components/Legend";
import { TestResults, Clients, Test } from "../types";
import testResultsData from "../data/test_results.json";
import clientsData from "../data/clients.json";
import { formatDate } from "../lib/utils";
import { Github } from "lucide-react";
import { config } from "../config/app";

function HomeContent() {
  const { tests, lastUpdated } = testResultsData as TestResults;
  const clients = clientsData as Clients;
  const router = useRouter();
  const searchParams = useSearchParams();

  const [selectedTest, setSelectedTest] = useState<Test | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Open modal from URL parameter on mount
  useEffect(() => {
    const testId = searchParams.get("test");
    if (testId) {
      const test = tests.find((t) => t.id === testId);
      if (test) {
        setSelectedTest(test);
        setIsModalOpen(true);
      }
    }
  }, [searchParams, tests]);

  const handleTestClick = (test: Test) => {
    setSelectedTest(test);
    setIsModalOpen(true);
    // Update URL with test ID
    router.push(`?test=${test.id}`, { scroll: false });
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedTest(null);
    // Remove test parameter from URL
    router.push("/", { scroll: false });
  };

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
      <div className="relative z-10 max-w-7xl mx-auto p-4">
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

        <Legend />

        <TestResultsTable
          tests={tests}
          clients={clients}
          lastUpdated={lastUpdated}
          onTestClick={handleTestClick}
        />

        <TestCaseDetailModal
          test={selectedTest}
          clients={clients}
          isOpen={isModalOpen}
          onClose={handleModalClose}
        />
        {/* Contribute link */}
        <div className="flex justify-center m-6">
          <a
            href={config.checklistUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-white/10 dark:bg-gray-800/20 border border-white/30 dark:border-gray-500/40 text-lime-500 hover:text-lime-400 hover:bg-white/15 dark:hover:bg-gray-800/30 transition-all duration-200 backdrop-blur-md group"
          >
            <Github
              size={16}
              className="group-hover:scale-110 transition-transform duration-200"
            />
            <span className="font-mono text-sm">Propose more test cases</span>
          </a>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-white dark:bg-gray-950" />}>
      <HomeContent />
    </Suspense>
  );
}
