import { Simulation } from "../config/app";

export type Status = "pass" | "fail" | "pending";

export interface Result {
  simulation: Simulation;
  status: Status;
}

export interface TestVariant {
  id: string;
  parameters?: Record<string, string>;
  results: Record<string, Result[]>;
}

export interface Test {
  id: string;
  description: string;
  setup: string;
  expectation: string;
  status: "completed" | "planned";
  results: Record<string, Result[]>; // aggregated from variants
  variants: TestVariant[];
}

export interface Client {
  id: string;
  name: string;
  hiveName: string;
  language: string;
  website: string;
  logo?: string;
  repo?: string;
  version: string;
  githubRepo?: string;
}

export interface TestResults {
  spec: string;
  lastUpdated: string;
  tests: Test[];
}

export type Clients = Client[];