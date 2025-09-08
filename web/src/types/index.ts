export interface Test {
  id: string;
  description: string;
  setup: string;
  expectation: string;
  status: "completed" | "planned";
  results: Record<string, "pass" | "fail" | "pending">;
}

export interface Client {
  id: string;
  name: string;
  hiveName: string;
  language: string;
  website: string;
  logo?: string;
  repo?: string;
}

export interface TestResults {
  spec: string;
  lastUpdated: string;
  tests: Test[];
}

export type Clients = Client[];