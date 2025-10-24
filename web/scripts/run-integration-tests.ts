#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { exec } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { config } from "../src/config/app";
import { parseHiveResults } from "./parse-hive-results";
import { Simulation } from "../src/config/app";

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
	const hiveResultsPath = path.resolve(__dirname, "../.hive");

	console.log("🧹 Clearing hive results directory...");

	if (fs.existsSync(hiveResultsPath)) {
		fs.rmSync(hiveResultsPath, { recursive: true, force: true });
	}

	fs.mkdirSync(hiveResultsPath, { recursive: true });
}

/**
 * Runs a single Hive simulation with configured clients and test filters
 * Results are output to the .hive directory in the web folder
 */
async function runHiveSimulation(simulation: Simulation) {
	const hiveResultsPath = path.resolve(__dirname, "../.hive", simulation);
	const hiveClientsPath = path.resolve(
		__dirname,
		"../src/data/hive_clients.yml",
	);

	// Create simulation-specific directory
	fs.mkdirSync(hiveResultsPath, { recursive: true });

	const hiveCommand = [
		`./hive --sim ${simulation}`,
		`--client-file=${hiveClientsPath}`,
		`--sim.buildarg fixtures=${config.hive.buildArgs.fixtures}`,
		`--sim.buildarg branch=${config.hive.buildArgs.branch}`,
		"--docker.output",
		`--results-root ${hiveResultsPath}`,
		`--sim.limit "${config.hive.testFilter}"`,
		`--sim.parallelism ${config.hive.parallelism}`,
		"2>/dev/null", // Redirect output to prevent maxBuffer overflow
	].join(" \\\n  ");

	console.log(`🚀 Running Hive simulation: ${simulation}`);
	console.log(`Command: ${hiveCommand}`);

	try {
		const { stdout, stderr } = await execAsync(hiveCommand, {
			cwd: HIVE_REPO_PATH,
		});
	} catch (error: any) {
		// console.err(
		// 	`❌ Error running Hive Simulation ${simulation} [error: ${error.message}]`,
		// );
	}
}

/**
 * Runs all configured Hive simulations sequentially and parses results after each
 */
async function runAllSimulations() {
	await clearHiveDirectory();
	for (const simulation of Object.values(Simulation)) {
		try {
			console.log(`\n🔄 Starting simulation: ${simulation}`);
			await runHiveSimulation(simulation);
			await parseHiveResults(simulation);
			console.log(`✅ Completed simulation: ${simulation}`);
		} catch (error) {
			console.error(`Failed to run simulation ${simulation}:`, error);
			throw error;
		}
	}
}

/**
 * Main execution function - verifies Hive installation and runs all simulations
 */
async function main() {
	try {
		console.log("🔄 Starting Hive integration test runner...");
		await verifyHiveInstallation();
		await runAllSimulations();
		console.log("✅ Integration test runner completed successfully");
	} catch (error: any) {
		console.error(error.message);
		process.exit(1);
	}
}

if (import.meta.url === `file://${process.argv[1]}`) {
	main();
}
