#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import https from 'https';
import { fileURLToPath } from 'url';
import { config } from '../src/config/app';
import { Result, Test as TestCase } from '../src/types';
import { Simulation } from '../src/config/app';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CHECKLIST_URL = config.checklistRawUrl;
const TEST_RESULTS_PATH = path.join(__dirname, '../src/data/test_results.json');

function fetchMarkdown(url: string): Promise<string> {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve(data);
      });
      
    }).on('error', (err) => {
      reject(err);
    });
  });
}

interface TablePosition {
  headerIndex: number;
  separatorIndex: number;
}

function validateMarkdown(content: string): TablePosition {
  const lines = content.split('\n');
  
  // Find table header
  const headerIndex = lines.findIndex(line => 
    line.includes('Function Name') && 
    line.includes('Goal') && 
    line.includes('Setup') && 
    line.includes('Expectation') && 
    line.includes('Status')
  );
  
  if (headerIndex === -1) {
    throw new Error('Table header with required columns not found');
  }
  
  // Validate table structure
  const separatorIndex = headerIndex + 1;
  if (separatorIndex >= lines.length || !lines[separatorIndex].includes('---')) {
    throw new Error('Invalid table separator');
  }
  
  return { headerIndex, separatorIndex };
}


function parseMarkdownTable(content: string): TestCase[] {
  const { headerIndex, separatorIndex } = validateMarkdown(content);
  const lines = content.split('\n');
  
  const testCases = [];
  
  // Parse table rows
  for (let i = separatorIndex + 1; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Stop if we hit an empty line or non-table content
    if (!line || !line.startsWith('|')) {
      break;
    }
    
    const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
    
    if (cells.length >= 5) {
      const [functionName, goal, setup, expectation, status] = cells;
      
      // Validate required fields
      if (!functionName || !goal || !setup || !expectation || !status) {
        console.warn(`Skipping row with empty cells: ${line}`);
        continue;
      }
      
      // Clean up status
      const cleanStatus: 'completed' | 'planned' = status.toLowerCase().includes('completed') || status.includes('✅') ? 'completed' : 'planned';

      // Only include completed tests
      if (cleanStatus === 'completed') {
        testCases.push({
          id: functionName.replace(/`/g, ''),
          description: goal,
          setup,
          expectation,
          status: cleanStatus,
          variants: []
        });
      }
    }
  }
  
  return testCases;
}

interface TestResults {
  spec: string;
  lastUpdated: string;
  tests: TestCase[];
}

function mergeTestResults(existingData: TestResults, newTestCases: TestCase[]): TestResults {
  return {
    ...existingData,
    lastUpdated: new Date().toISOString(),
    tests: newTestCases
  };
}

async function main() {
  try {
    console.log('🔄 Fetching markdown checklist...');
    const markdown = await fetchMarkdown(CHECKLIST_URL);
    
    console.log('📋 Parsing test cases...');
    const testCases = parseMarkdownTable(markdown);
    console.log(`✅ Parsed ${testCases.length} test cases`);
    
    console.log('📖 Reading existing test results...');
    const existingData = JSON.parse(fs.readFileSync(TEST_RESULTS_PATH, 'utf8'));
    
    console.log('🔄 Merging test cases...');
    const mergedData = mergeTestResults(existingData, testCases);
    
    console.log('💾 Writing updated test results...');
    fs.writeFileSync(TEST_RESULTS_PATH, JSON.stringify(mergedData, null, 2));
    
    console.log('🎉 Test cases synced successfully!');
    console.log(`   - Total tests: ${mergedData.tests.length}`);
    console.log(`   - New/updated: ${testCases.length}`);
    
  } catch (error) {
    console.error('❌ Error syncing test cases:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { fetchMarkdown, parseMarkdownTable, mergeTestResults };