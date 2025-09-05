import clientsData from "../data/clients.json";

export const config = {
  baseGithubUrl:
    "https://github.com/ethereum/execution-spec-tests/blob/main/tests/amsterdam/eip7928_block_level_access_lists/test_cases.md",
  get checklistRawUrl() {
    return this.baseGithubUrl
      .replace("github.com", "raw.githubusercontent.com")
      .replace("/blob", "");
  },
  get checklistUrl() {
    return this.baseGithubUrl;
  },
  hive: {
    // See: https://eest.ethereum.org/main/running_tests/hive/common_options/
    get clients() {
      return clientsData.map(client => client.hiveName);
    },
    buildArgs: {
      fixtures: "stable@v4.5.0",
      branch: "v4.5.0",
    },
    // TODO: Replace with BAL tests once PRs are merged
    testFilter: "id:tests/amsterdam/eip7928_block_level_access_lists/test_block_access_lists",
  },
};
