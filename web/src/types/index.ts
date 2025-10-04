import { Simulation } from "../config/app";

export type Status = "pass" | "fail" | "pending";

export interface Result {
  simulation: Simulation;
  status: Status;
}

export interface TestVariant {
  parameters?: string[];
  results: Record<string, Result[]>;
}

export interface Test {
  id: string;
  description: string;
  setup: string;
  expectation: string;
  status: "completed" | "planned";
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