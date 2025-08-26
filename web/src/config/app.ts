export const config = {
  baseGithubUrl:
    "https://github.com/ethereum/execution-spec-tests/blob/feat/eip-7928/checklist/tests/unscheduled/eip7928_block_level_access_lists/checklist.md",
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
    clients: ["go-ethereum"],
    buildArgs: {
      fixtures: "stable@v4.5.0",
      branch: "v4.5.0",
    },
    // TODO: Replace with BAL tests once PRs are merged
    testFilter: "id:tests/shanghai/eip3855_push0/test_push0.py",
  },
};
