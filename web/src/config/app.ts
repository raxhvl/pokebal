export const config = {
  baseGithubUrl: "https://github.com/ethereum/execution-spec-tests/blob/feat/eip-7928/checklist/tests/unscheduled/eip7928_block_level_access_lists/checklist.md",
  get checklistRawUrl() {
    return this.baseGithubUrl.replace("github.com", "raw.githubusercontent.com").replace("/blob", "");
  },
  get checklistUrl() {
    return this.baseGithubUrl;
  }
};