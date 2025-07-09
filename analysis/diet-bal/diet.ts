import {
	existsSync,
	mkdirSync,
	readdirSync,
	readFileSync,
	writeFileSync,
} from "node:fs";
import { join } from "node:path";
import { compressSync } from "snappy";

import {
	ByteListType,
	ByteVectorType,
	ContainerType,
	ListBasicType,
	ListCompositeType,
	UintBigintType,
	UintNumberType,
} from "@chainsafe/ssz";

const MAX_TXS = 30_000;
const MAX_SLOTS = 300_000;
const MAX_ACCOUNTS = 300_000;
const MAX_CODE_SIZE = 24_576;

const SOURCE_BAL_DIR = "data/analysis/bal";
const TARGET_DIR = "data/analysis/diet-bal";

const StorageChange = new ContainerType({
	txIndex: new UintNumberType(2),
	newValue: new ByteVectorType(32),
});

const SlotChanges = new ContainerType({
	slot: new ByteVectorType(32),
	changes: new ListCompositeType(StorageChange, MAX_TXS),
});

const BalanceChange = new ContainerType({
	txIndex: new UintNumberType(2),
	newBalance: new UintBigintType(16),
});

const NonceChange = new ContainerType({
	txIndex: new UintNumberType(2),
	newNonce: new UintNumberType(8),
});

const CodeChange = new ContainerType({
	txIndex: new UintNumberType(2),
	newCode: new ByteListType(MAX_CODE_SIZE),
});

const AccountChanges = new ContainerType({
	address: new ByteVectorType(20),
	storageChanges: new ListCompositeType(SlotChanges, MAX_SLOTS),
	storageReads: new ListCompositeType(new ByteVectorType(32), MAX_SLOTS),
	balanceChanges: new ListCompositeType(BalanceChange, MAX_TXS),
	nonceChanges: new ListCompositeType(NonceChange, MAX_TXS),
	codeChanges: new ListCompositeType(CodeChange, MAX_TXS),
});

export const BlockAccessLists = new ContainerType({
	accountChanges: new ListCompositeType(AccountChanges, MAX_ACCOUNTS),
});

const TransactionBatch = new ListBasicType(new UintNumberType(2), MAX_TXS);

const DietAccount = new ContainerType({
	address: new ByteVectorType(20),
	slots: new ListCompositeType(new ByteVectorType(32), MAX_SLOTS),
});

export const DietBlockAccessLists = new ContainerType({
	accounts: new ListCompositeType(DietAccount, MAX_ACCOUNTS),
	transactionBatches: new ListCompositeType(TransactionBatch, MAX_TXS),
});

export function convertBalToDietBal(bal: any): any {
	const dietAccounts = [];
	const allTransactions = new Map<number, TransactionWrites>();

	for (const accountChange of bal.accountChanges) {
		const slots = new Set<string>();

		accountChange.storageChanges.forEach((sc) => slots.add(sc.slot));
		accountChange.storageReads.forEach((slot) => slots.add(slot));

		dietAccounts.push({
			address: accountChange.address,
			slots: Array.from(slots),
		});

		collectTransactionsForAccount(accountChange, allTransactions);
	}

	return {
		accounts: dietAccounts,
		transactionBatches: createGlobalBatches(
			Array.from(allTransactions.values()),
		),
	};
}

interface TransactionWrites {
	txIndex: number;
	accountAddress: string;
	storageSlots: Set<string>;
	writesBalance: boolean;
	writesNonce: boolean;
	writesCode: boolean;
}

function collectTransactionsForAccount(
	accountChange: any,
	allTransactions: Map<number, TransactionWrites>,
): void {
	const accountAddress = accountChange.address.toString();

	const getOrCreateTransaction = (txIndex: number): TransactionWrites => {
		if (!allTransactions.has(txIndex)) {
			allTransactions.set(txIndex, {
				txIndex,
				accountAddress,
				storageSlots: new Set(),
				writesBalance: false,
				writesNonce: false,
				writesCode: false,
			});
		}
		return allTransactions.get(txIndex)!;
	};

	accountChange.storageChanges.forEach((sc) => {
		const slotKey = `${accountAddress}:${sc.slot}`;
		sc.changes.forEach((change) => {
			getOrCreateTransaction(change.txIndex).storageSlots.add(slotKey);
		});
	});

	accountChange.balanceChanges.forEach((bc) => {
		getOrCreateTransaction(bc.txIndex).writesBalance = true;
	});

	accountChange.nonceChanges.forEach((nc) => {
		getOrCreateTransaction(nc.txIndex).writesNonce = true;
	});

	accountChange.codeChanges.forEach((cc) => {
		getOrCreateTransaction(cc.txIndex).writesCode = true;
	});
}

function createGlobalBatches(transactions: TransactionWrites[]): number[][] {
	transactions.sort((a, b) => a.txIndex - b.txIndex);

	const batches: number[][] = [];
	const processed = new Set<number>();

	while (processed.size < transactions.length) {
		const currentBatch: number[] = [];
		const usedResources = {
			storageSlots: new Set<string>(),
			accountBalances: new Set<string>(),
			accountNonces: new Set<string>(),
			accountCodes: new Set<string>(),
		};

		for (const tx of transactions) {
			if (processed.has(tx.txIndex)) continue;

			const conflicts =
				[...tx.storageSlots].some((slot) =>
					usedResources.storageSlots.has(slot),
				) ||
				(tx.writesBalance &&
					usedResources.accountBalances.has(tx.accountAddress)) ||
				(tx.writesNonce &&
					usedResources.accountNonces.has(tx.accountAddress)) ||
				(tx.writesCode && usedResources.accountCodes.has(tx.accountAddress));

			if (!conflicts) {
				currentBatch.push(tx.txIndex);
				processed.add(tx.txIndex);

				tx.storageSlots.forEach((slot) => usedResources.storageSlots.add(slot));
				if (tx.writesBalance)
					usedResources.accountBalances.add(tx.accountAddress);
				if (tx.writesNonce) usedResources.accountNonces.add(tx.accountAddress);
				if (tx.writesCode) usedResources.accountCodes.add(tx.accountAddress);
			}
		}

		if (currentBatch.length > 0) {
			batches.push(currentBatch);
		}
	}

	return batches;
}

export function convert(
	filePaths: string[],
	enableCompression: boolean = false,
): void {
	mkdirSync(TARGET_DIR, { recursive: true });

	if (enableCompression) {
		mkdirSync(join(SOURCE_BAL_DIR, "compressed"), { recursive: true });
		mkdirSync(join(TARGET_DIR, "compressed"), { recursive: true });
	}

	for (const sourcePath of filePaths) {
		const filename = sourcePath.split("/").pop() || sourcePath;
		const targetPath = join(TARGET_DIR, filename);

		try {
			const rawData = readFileSync(sourcePath);
			const bal = BlockAccessLists.deserialize(rawData);
			const dietBal = convertBalToDietBal(bal);
			const serialized = DietBlockAccessLists.serialize(dietBal);
			writeFileSync(targetPath, serialized);

			console.log(`Converted ${filename}`);

			if (enableCompression) {
				const compressedBalPath = join(
					SOURCE_BAL_DIR,
					"compressed",
					filename.replace(".ssz", ".ssz.snappy"),
				);
				if (!existsSync(compressedBalPath)) {
					writeFileSync(compressedBalPath, compressSync(rawData));
					console.log(`Compressed BAL ${filename}`);
				}

				const compressedDietBalPath = join(
					TARGET_DIR,
					"compressed",
					filename.replace(".ssz", ".ssz.snappy"),
				);
				writeFileSync(compressedDietBalPath, compressSync(serialized));
				console.log(`Compressed Diet BAL ${filename}`);
			}
		} catch (error) {
			console.error(`Error converting ${filename}:`, error);
		}
	}
}

export interface StatsResult {
	bal: {
		ssz: Record<string, number>;
		compressed?: Record<string, number>;
	};
	dietBal: {
		ssz: Record<string, number>;
		compressed?: Record<string, number>;
	};
}

export function stats(
	filePaths: string[],
	includeCompressed: boolean = false,
): StatsResult {
	const result: StatsResult = {
		bal: { ssz: {}, ...(includeCompressed && { compressed: {} }) },
		dietBal: { ssz: {}, ...(includeCompressed && { compressed: {} }) },
	};

	for (const sourcePath of filePaths) {
		const filename = sourcePath.split("/").pop() || sourcePath;
		const targetPath = join(TARGET_DIR, filename);

		try {
			result.bal.ssz[filename] = readFileSync(sourcePath).length;
			result.dietBal.ssz[filename] = readFileSync(targetPath).length;

			if (includeCompressed) {
				const compressedBalPath = join(
					SOURCE_BAL_DIR,
					"compressed",
					filename.replace(".ssz", ".ssz.snappy"),
				);
				const compressedDietBalPath = join(
					TARGET_DIR,
					"compressed",
					filename.replace(".ssz", ".ssz.snappy"),
				);

				if (existsSync(compressedBalPath)) {
					result.bal.compressed![filename] =
						readFileSync(compressedBalPath).length;
				}
				if (existsSync(compressedDietBalPath)) {
					result.dietBal.compressed![filename] = readFileSync(
						compressedDietBalPath,
					).length;
				}
			}
		} catch (error) {
			console.error(`Error analyzing ${filename}:`, error);
		}
	}

	return result;
}

export function analyse(): StatsResult {
	const sszFiles = readdirSync(SOURCE_BAL_DIR)
		.filter((file) => file.endsWith(".ssz"))
		.map((file) => join(SOURCE_BAL_DIR, file));

	convert(sszFiles, true);
	return stats(sszFiles, true);
}
