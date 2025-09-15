#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { Client, Test, TestResults } from '../src/types/index';

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



function loadClientMappings(): Record<string, string> {
  const clientsPath = path.join(process.cwd(), 'src', 'data', 'clients.json');
  const clientsRaw = fs.readFileSync(clientsPath, 'utf8');
  const clients: Client[] = JSON.parse(clientsRaw);

  const mappings: Record<string, string> = {};
  clients.forEach(client => {
    mappings[client.hiveName] = client.id;
  });

  return mappings;
}

const CLIENT_MAPPINGS = loadClientMappings();

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


function extractTestInfo(testName: string): { baseTest: string; client: string } | null {
  // Build regex from client mappings
  const hiveClientNames = Object.keys(CLIENT_MAPPINGS).join('|');
  const clientRegex = new RegExp(`-(${hiveClientNames})$`);

  const clientMatch = testName.match(clientRegex);
  if (!clientMatch) return null;

  const hiveClient = clientMatch[1];
  const client = CLIENT_MAPPINGS[hiveClient];
  if (!client) return null;

  // Remove client suffix to get base test name
  const baseTestWithParams = testName.replace(`-${hiveClient}`, '');

  // Extract the actual test function name from the path
  // Format: tests/amsterdam/eip7928_block_level_access_lists/test_block_access_lists.py::test_bal_nonce_changes[fork_Amsterdam-blockchain_test]
  const testFunctionMatch = baseTestWithParams.match(/::([^[]+)/);
  if (!testFunctionMatch) return null;

  const baseTest = testFunctionMatch[1];

  return { baseTest, client };
}

function mapHiveResultToTestResult(
  hiveResults: HiveResults,
  existingTestResults: TestResults
): TestResults {
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
  
  // Match tests by name and update results
  Object.entries(processedResults).forEach(([hiveTestName, clientResults]) => {
    const testIndex = updatedTests.findIndex(test => test.id === hiveTestName);

    if (testIndex !== -1) {
      // Update results for all clients that have results
      Object.entries(clientResults).forEach(([client, passed]) => {
        if (updatedTests[testIndex].results[client] !== undefined) {
          updatedTests[testIndex].results[client] = passed ? 'pass' : 'fail';
        }
      });
      console.log(`✓ Updated ${hiveTestName}`);
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
    const testResults: TestResults = JSON.parse(testResultsRaw);

    console.log(`Hive test suite: ${hiveResults.name}`);
    console.log(`Hive description: ${hiveResults.description}`);
    console.log(`Current test spec: ${testResults.spec}`);

    // Parse and update results
    const updatedResults = mapHiveResultToTestResult(hiveResults, testResults);
    
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
  extractTestInfo,
  mapHiveResultToTestResult,
  findHiveResultsFile
};