export interface Test {
  id: string;
  name: string;
  description: string;
  results: Record<string, "pass" | "fail" | "not_implemented">;
}

export interface Client {
  id: string;
  name: string;
  language: string;
  website: string;
  logo?: string;
}

export interface TestResults {
  spec: string;
  lastUpdated: string;
  tests: Test[];
}

export type Clients = Client[];