#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { exec } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { config } from "../src/config/app.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const execAsync = promisify(exec);
const HIVE_REPO_PATH = process.env.HIVE_REPO_PATH || "/tmp/hive";

/**
 * Verifies that Hive CLI is installed and accessible
 */
async function verifyHiveInstallation() {
  try {
    await execAsync("./hive --cleanup", { cwd: HIVE_REPO_PATH });
  } catch (error: any) {
    throw new Error(
      `❌ Hive CLI not found. Please install Hive first [error: ${error.message}]`,
    );
  }
}

/**
 * Clears the .hive directory to ensure clean test runs
 */
async function clearHiveDirectory() {
  const hiveResultsPath = path.join(__dirname, "../.hive");
  
  console.log("🧹 Clearing hive results directory...");
  
  if (fs.existsSync(hiveResultsPath)) {
    fs.rmSync(hiveResultsPath, { recursive: true, force: true });
  }
  
  fs.mkdirSync(hiveResultsPath, { recursive: true });
}

/**
 * Runs Hive simulations with ethereum/eest/consume-engine using configured clients and test filters
 * Results are output to the .hive directory in the web folder
 */
async function runHiveSimulations() {
  const hiveResultsPath = path.join(__dirname, "../.hive");
  const hiveCommand = [
    "./hive --sim ethereum/eest/consume-engine",
    `--client ${config.hive.clients.join(",")}`,
    `--sim.buildarg fixtures=${config.hive.buildArgs.fixtures}`,
    `--sim.buildarg branch=${config.hive.buildArgs.branch}`,
    "--docker.output",
    `--results-root ${hiveResultsPath}`,
    `--sim.limit "${config.hive.testFilter}"`,
  ].join(" \\\n  ");

  console.log("🚀 Running Hive simulation...");
  console.log(`Command: ${hiveCommand}`);

  try {
    await execAsync(hiveCommand, { cwd: HIVE_REPO_PATH });
  } catch (error: any) {
    throw new Error(
      `❌ Error running Hive Simulations [error: ${error.message}]`,
    );
  }
}

/**
 * Main execution function - verifies Hive installation and runs simulations
 */
async function main() {
  try {
    console.log("🔄 Starting Hive integration test runner...");
    await verifyHiveInstallation();
    await clearHiveDirectory();
    await runHiveSimulations();
    console.log("✅ Integration test runner completed successfully");
  } catch (error: any) {
    console.error(error.message);
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
