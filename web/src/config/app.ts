export enum Simulation {
	ConsumeRLP = "consume-rlp",
	ConsumeEngine = "consume-engine",
}

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
		parallelism: 4,
		buildArgs: {
			fixtures: "bal@v1.3.0",
			branch: "forks/amsterdam",
		},
		testFilter: "id:tests/amsterdam/eip7928_block_level_access_lists",
		clientConfig: "src/data/hive_config.yml",
	},
};
