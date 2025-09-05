#!/usr/bin/env node

import fs from 'fs';
import path from 'path';

interface HiveTestCase {
  name: string;
  description: string;
  start: string;
  end: string;
  summaryResult: {
    pass: boolean;
    log?: {
      begin: number;
      end: number;
    };
  };
  clientInfo: Record<string, any>;
}

interface HiveResults {
  id: number;
  name: string;
  description: string;
  clientVersions: Record<string, string>;
  runMetadata: {
    hiveCommand: string[];
    hiveVersion: {
      commit: string;
      commitDate: string;
      branch: string;
    };
  };
  testCases: Record<string, HiveTestCase>;
}

interface TestResult {
  id: string;
  description: string;
  setup: string;
  expectation: string;
  status: string;
  results: Record<string, string>;
}

interface TestResultsJson {
  spec: string;
  lastUpdated: string;
  tests: TestResult[];
}

// Map Hive client names to our client names
const CLIENT_MAPPINGS = {
  'go-ethereum': 'geth',
  'nethermind': 'nethermind',
  'besu': 'besu',
  'erigon': 'erigon',
  'reth': 'reth'
} as const;

function findHiveResultsFile(hiveDir: string): string | null {
  try {
    const files = fs.readdirSync(hiveDir);
    // Find JSON file with hyphen in name (excluding hive.json)
    const hiveResultFile = files.find(file => 
      file.endsWith('.json') && 
      file.includes('-') && 
      file !== 'hive.json'
    );
    
    return hiveResultFile ? path.join(hiveDir, hiveResultFile) : null;
  } catch (error) {
    console.error('Error reading hive directory:', error);
    return null;
  }
}

function parseClientFromTestName(testName: string): string | null {
  // Test names end with "-{client}"
  const match = testName.match(/-([^-]+)$/);
  if (!match) return null;
  
  const hiveClient = match[1];
  return CLIENT_MAPPINGS[hiveClient as keyof typeof CLIENT_MAPPINGS] || null;
}

function extractTestInfo(testName: string): { baseTest: string; client: string } | null {
  // Extract client from end
  const clientMatch = testName.match(/-([^-]+)$/);
  if (!clientMatch) return null;
  
  const hiveClient = clientMatch[1];
  const client = CLIENT_MAPPINGS[hiveClient as keyof typeof CLIENT_MAPPINGS];
  if (!client) return null;
  
  // Remove client suffix to get base test name
  const baseTest = testName.replace(`-${hiveClient}`, '');
  
  return { baseTest, client };
}

function mapHiveResultToTestResult(
  hiveResults: HiveResults,
  existingTestResults: TestResultsJson,
  testMapping: Record<string, string> = {}
): TestResultsJson {
  const updatedTests = [...existingTestResults.tests];
  const processedResults: Record<string, Record<string, boolean>> = {};
  
  console.log(`Processing ${Object.keys(hiveResults.testCases).length} test cases...`);
  console.log(`Client versions:`, hiveResults.clientVersions);
  
  // Group test results by base test name
  Object.values(hiveResults.testCases).forEach(testCase => {
    const testInfo = extractTestInfo(testCase.name);
    if (!testInfo) {
      console.warn(`Could not parse test info from: ${testCase.name}`);
      return;
    }
    
    const { baseTest, client } = testInfo;
    
    if (!processedResults[baseTest]) {
      processedResults[baseTest] = {};
    }
    
    processedResults[baseTest][client] = testCase.summaryResult.pass;
    console.log(`${baseTest} [${client}]: ${testCase.summaryResult.pass ? 'PASS' : 'FAIL'}`);
  });
  
  console.log(`\nGrouped into ${Object.keys(processedResults).length} unique test groups`);
  
  // Apply mapping if provided, otherwise try to match existing tests
  Object.entries(processedResults).forEach(([hiveTestName, clientResults]) => {
    let matchingTestId: string | null = null;
    
    // Check if we have an explicit mapping
    if (testMapping[hiveTestName]) {
      matchingTestId = testMapping[hiveTestName];
    } else {
      // Try to find a matching test in existing results
      // Since the current tests are BAL tests and hive has PUSH0 tests,
      // this will likely not find matches until proper BAL tests are run
      const matchingTest = updatedTests.find(test => {
        const testId = test.id.toLowerCase();
        const hiveName = hiveTestName.toLowerCase();
        
        // Try various matching strategies
        return (
          testId.includes(hiveName) ||
          hiveName.includes(testId) ||
          // Extract test method name and compare
          (() => {
            const methodMatch = hiveName.match(/::([^:\[]+)/);
            return methodMatch && testId.includes(methodMatch[1].toLowerCase());
          })()
        );
      });
      
      if (matchingTest) {
        matchingTestId = matchingTest.id;
      }
    }
    
    if (matchingTestId) {
      const testIndex = updatedTests.findIndex(test => test.id === matchingTestId);
      if (testIndex !== -1) {
        // Update results for all clients that have results
        Object.entries(clientResults).forEach(([client, passed]) => {
          if (updatedTests[testIndex].results[client] !== undefined) {
            updatedTests[testIndex].results[client] = passed ? 'pass' : 'fail';
          }
        });
        console.log(`✓ Updated ${matchingTestId} with results from ${hiveTestName}`);
      }
    } else {
      console.log(`⚠ No matching test found for: ${hiveTestName}`);
    }
  });
  
  return {
    ...existingTestResults,
    lastUpdated: new Date().toISOString(),
    tests: updatedTests
  };
}

// Example test mapping - you would customize this based on your actual test relationships
const DEFAULT_TEST_MAPPING: Record<string, string> = {
  // Example: map hive test names to test_results.json test IDs
  // "tests/shanghai/eip3855_push0/test_push0.py::test_some_function": "test_bal_some_feature",
};

async function main() {
  const webDir = process.cwd();
  const hiveDir = path.join(webDir, '.hive');
  const testResultsPath = path.join(webDir, 'src', 'data', 'test_results.json');
  
  // Find hive results file
  const hiveResultsPath = findHiveResultsFile(hiveDir);
  if (!hiveResultsPath) {
    console.error('No hive results file found in .hive directory');
    process.exit(1);
  }
  
  console.log(`Found hive results: ${path.basename(hiveResultsPath)}`);
  
  try {
    // Load hive results
    const hiveResultsRaw = fs.readFileSync(hiveResultsPath, 'utf8');
    const hiveResults: HiveResults = JSON.parse(hiveResultsRaw);
    
    // Load existing test results
    const testResultsRaw = fs.readFileSync(testResultsPath, 'utf8');
    const testResults: TestResultsJson = JSON.parse(testResultsRaw);
    
    console.log(`Hive test suite: ${hiveResults.name}`);
    console.log(`Hive description: ${hiveResults.description}`);
    console.log(`Current test spec: ${testResults.spec}`);
    
    // Parse and update results
    const updatedResults = mapHiveResultToTestResult(hiveResults, testResults, DEFAULT_TEST_MAPPING);
    
    // Write updated results
    fs.writeFileSync(
      testResultsPath, 
      JSON.stringify(updatedResults, null, 2)
    );
    
    console.log('\n✅ Updated test_results.json successfully');
    
    // Print summary
    const totalUpdates = updatedResults.tests.reduce((count, test) => {
      return count + Object.values(test.results).filter(result => result !== 'pending').length;
    }, 0);
    
    console.log(`📊 Total result updates: ${totalUpdates}`);
    
    // Show update summary per client
    const clientSummary: Record<string, { pass: number; fail: number }> = {};
    updatedResults.tests.forEach(test => {
      Object.entries(test.results).forEach(([client, result]) => {
        if (result !== 'pending') {
          if (!clientSummary[client]) {
            clientSummary[client] = { pass: 0, fail: 0 };
          }
          if (result === 'pass') {
            clientSummary[client].pass++;
          } else {
            clientSummary[client].fail++;
          }
        }
      });
    });
    
    console.log('\n📈 Results summary by client:');
    Object.entries(clientSummary).forEach(([client, summary]) => {
      console.log(`  ${client}: ${summary.pass} pass, ${summary.fail} fail`);
    });
    
  } catch (error) {
    console.error('Error processing results:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { 
  parseClientFromTestName, 
  extractTestInfo, 
  mapHiveResultToTestResult,
  findHiveResultsFile
};