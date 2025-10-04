import fs from 'fs';
import path from 'path';
import { parse as parseYaml } from 'yaml';
import { Client, Test, TestResults } from '../src/types/index';
import { Simulation } from '../src/config/app';

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

interface HiveClientConfig {
  client: string;
  dockerfile: string;
  build_args: {
    github: string;
    tag: string;
  };
}

function loadHiveClientConfigs(): Record<string, string> {
  const hiveClientsPath = path.join(process.cwd(), 'src', 'data', 'hive_clients.yml');
  const hiveClientsRaw = fs.readFileSync(hiveClientsPath, 'utf8');
  const hiveClients = parseYaml(hiveClientsRaw) as HiveClientConfig[];

  const githubRepos: Record<string, string> = {};
  hiveClients.forEach(config => {
    githubRepos[config.client] = `https://github.com/${config.build_args.github}/tree/${config.build_args.tag}`;
  });

  return githubRepos;
}

function updateClientVersions(clientVersions: Record<string, string>) {
  const clientsPath = path.join(process.cwd(), 'src', 'data', 'clients.json');
  const clientsRaw = fs.readFileSync(clientsPath, 'utf8');
  const clients: Client[] = JSON.parse(clientsRaw);

  // Load GitHub repo information from hive_clients.yml
  const githubRepos = loadHiveClientConfigs();

  // Update clients with version and GitHub repo information
  const updatedClients = clients.map(client => ({
    ...client,
    version: clientVersions[client.hiveName] || "unknown",
    githubRepo: githubRepos[client.hiveName]
  }));

  // Write updated clients back to file
  fs.writeFileSync(clientsPath, JSON.stringify(updatedClients, null, 2));
  console.log('✅ Updated clients.json with version and GitHub repository information');
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


function extractTestInfo(testName: string): { baseTest: string; parameters?: string[]; client: string } | null {
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

  // Extract the test function name and parameters from the path
  // Format: tests/amsterdam/eip7928_block_level_access_lists/test_block_access_lists.py::test_bal_nonce_changes[fork_Amsterdam-blockchain_test]
  const testFunctionMatch = baseTestWithParams.match(/::([^[]+)(\[([^\]]+)\])?/);
  if (!testFunctionMatch) return null;

  const baseTest = testFunctionMatch[1];
  const paramString = testFunctionMatch[3];

  // Parse parameters if present
  let parameters: string[] | undefined;
  if (paramString) {
    // Split by dash and filter out simulation artifacts
    const parts = paramString.split('-');
    const filteredParts = parts.filter(part =>
      part !== 'blockchain_test' && part !== 'blockchain_test_engine'
    );

    // Only include if we have actual parameters
    if (filteredParts.length > 0) {
      parameters = filteredParts;
    }
  }

  return { baseTest, parameters, client };
}


function mapHiveResultToTestResult(
  hiveResults: HiveResults,
  existingTestResults: TestResults,
  simulationType: Simulation
): TestResults {
  const updatedTests = [...existingTestResults.tests];

  // Group test results by base test name and actual parameter variations
  const groupedResults: Record<string, Record<string, any>> = {};

  console.log(`Processing ${Object.keys(hiveResults.testCases).length} test cases...`);
  console.log(`Client versions:`, hiveResults.clientVersions);

  Object.values(hiveResults.testCases).forEach(testCase => {
    const testInfo = extractTestInfo(testCase.name);
    if (!testInfo) {
      console.warn(`Could not parse test info from: ${testCase.name}`);
      return;
    }

    const { baseTest, parameters, client } = testInfo;

    // Create a variant key based on actual parameters (not simulation artifacts)
    const variantKey = parameters
      ? JSON.stringify(parameters) // Use parameter signature as key
      : 'standalone'; // No parameters = standalone test

    if (!groupedResults[baseTest]) {
      groupedResults[baseTest] = {};
    }
    if (!groupedResults[baseTest][variantKey]) {
      groupedResults[baseTest][variantKey] = {
        parameters,
        results: {}
      };
    }

    // Determine simulation type from the original test name
    const isEngineSimulation = testCase.name.includes('blockchain_test_engine');
    const simulationType = isEngineSimulation ? 'consume-engine' : 'consume-rlp';

    // Initialize client results if not exists
    if (!groupedResults[baseTest][variantKey].results[client]) {
      groupedResults[baseTest][variantKey].results[client] = {};
    }

    groupedResults[baseTest][variantKey].results[client][simulationType] = testCase.summaryResult.pass;
    console.log(`${baseTest} [${variantKey}] [${client}] [${simulationType}]: ${testCase.summaryResult.pass ? 'PASS' : 'FAIL'}`);
  });

  console.log(`\nGrouped into ${Object.keys(groupedResults).length} base tests`);

  // Process each base test
  Object.entries(groupedResults).forEach(([baseTestName, variants]) => {
    const testIndex = updatedTests.findIndex(test => test.id === baseTestName);

    if (testIndex !== -1) {
      const test = updatedTests[testIndex];

      // Ensure test has variants array
      if (!test.variants) {
        test.variants = [];
      }

      // Process each variant
      Object.entries(variants).forEach(([variantKey, variantData]: [string, any]) => {
        const { parameters, results } = variantData;

        // Find or create variant by matching parameters
        let variant = test.variants.find(v =>
          JSON.stringify(v.parameters || []) === JSON.stringify(parameters || [])
        );
        if (!variant) {
          variant = {
            parameters: parameters || [],
            results: {}
          };
          test.variants.push(variant);
        }

        // Convert the flat simulation results to the expected format
        Object.entries(results).forEach(([client, simulations]: [string, any]) => {
          if (!variant!.results[client]) {
            variant!.results[client] = [];
          }

          // Process each simulation type
          Object.entries(simulations).forEach(([simType, passed]: [string, any]) => {
            // Find or create result for this simulation
            let result = variant!.results[client].find((r: any) => r.simulation === simType);
            if (!result) {
              result = { simulation: simType as Simulation, status: 'pending' };
              variant!.results[client].push(result);
            }

            result.status = passed ? 'pass' : 'fail';
          });
        });
      });

      console.log(`✓ Updated ${baseTestName} with ${test.variants.length} variants`);
    } else {
      console.log(`⚠ No matching test found for: ${baseTestName}`);
    }
  });

  return {
    ...existingTestResults,
    lastUpdated: new Date().toISOString(),
    tests: updatedTests
  };
}


export async function parseHiveResults(simulationType: Simulation) {
  const webDir = process.cwd();
  const hiveDir = path.join(webDir, '.hive');
  const testResultsPath = path.join(webDir, 'src', 'data', 'test_results.json');

  // Find hive results file
  const hiveResultsPath = findHiveResultsFile(hiveDir);
  if (!hiveResultsPath) {
    throw new Error('No hive results file found in .hive directory');
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

    // Update client versions
    updateClientVersions(hiveResults.clientVersions);

    // Parse and update results
    const updatedResults = mapHiveResultToTestResult(hiveResults, testResults, simulationType);

    // Write updated results
    fs.writeFileSync(
      testResultsPath,
      JSON.stringify(updatedResults, null, 2)
    );

    console.log('\n✅ Updated test_results.json successfully');

    // Print summary
    let totalUpdates = 0;
    const clientSummary: Record<string, { pass: number; fail: number }> = {};

    updatedResults.tests.forEach(test => {
      test.variants.forEach(variant => {
        Object.entries(variant.results).forEach(([client, results]) => {
          results.forEach(result => {
            if (result.simulation === simulationType && result.status !== 'pending') {
              totalUpdates++;
              if (!clientSummary[client]) {
                clientSummary[client] = { pass: 0, fail: 0 };
              }
              if (result.status === 'pass') {
                clientSummary[client].pass++;
              } else {
                clientSummary[client].fail++;
              }
            }
          });
        });
      });
    });

    console.log(`📊 Total result updates for ${simulationType}: ${totalUpdates}`);

    console.log('\n📈 Results summary by client:');
    Object.entries(clientSummary).forEach(([client, summary]) => {
      console.log(`  ${client}: ${summary.pass} pass, ${summary.fail} fail`);
    });

  } catch (error) {
    console.error('Error processing results:', error);
    throw error;
  }
}

