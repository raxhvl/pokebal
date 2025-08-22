export interface Test {
  id: string;
  name: string;
  description: string;
  category: string;
}

export interface Client {
  id: string;
  name: string;
  language: string;
  website: string;
  logo?: string;
  testResults: Record<string, "pass" | "fail" | "not_implemented">;
}

export interface ClientsData {
  spec: string;
  tests: Test[];
  clients: Client[];
}