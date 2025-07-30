import { BaselineBlockAccessLists } from "./schemas/baseline";
import { CompactBlockAccessLists } from "./schemas/compact";

type BaselineData = ReturnType<typeof BaselineBlockAccessLists.defaultValue>;
type CompactData = ReturnType<typeof CompactBlockAccessLists.defaultValue>;

export function baselineToCompact(baseline: BaselineData): CompactData {
    const accountMap = new Map<string, any>();

    for (const accountChange of baseline.accountChanges) {
        const address = accountChange.address;
        const addressKey = Buffer.from(address).toString('hex');
        
        if (!accountMap.has(addressKey)) {
            accountMap.set(addressKey, {
                address,
                transactions: new Map<number, any[]>()
            });
        }
        
        const account = accountMap.get(addressKey)!;

        // Process nonce changes
        for (const nonceChange of accountChange.nonceChanges) {
            const txIndex = nonceChange.txIndex;
            if (!account.transactions.has(txIndex)) {
                account.transactions.set(txIndex, []);
            }
            account.transactions.get(txIndex)!.push({
                selector: 0, // Nonce Update
                value: nonceChange.newNonce
            });
        }

        // Process balance changes
        for (const balanceChange of accountChange.balanceChanges) {
            const txIndex = balanceChange.txIndex;
            if (!account.transactions.has(txIndex)) {
                account.transactions.set(txIndex, []);
            }
            account.transactions.get(txIndex)!.push({
                selector: 1, // Balance Update
                value: balanceChange.newBalance
            });
        }

        // Process code changes
        for (const codeChange of accountChange.codeChanges) {
            const txIndex = codeChange.txIndex;
            if (!account.transactions.has(txIndex)) {
                account.transactions.set(txIndex, []);
            }
            account.transactions.get(txIndex)!.push({
                selector: 2, // Code Update
                value: codeChange.newCode
            });
        }

        // Process storage changes
        for (const slotChange of accountChange.storageChanges) {
            const storageWrites = slotChange.changes.map(change => ({
                key: slotChange.slot,
                value: change.newValue
            }));
            
            for (const change of slotChange.changes) {
                const txIndex = change.txIndex;
                if (!account.transactions.has(txIndex)) {
                    account.transactions.set(txIndex, []);
                }
                
                // Find existing storage updates for this tx or create new
                let storageUpdateInteraction = account.transactions.get(txIndex)!
                    .find(interaction => interaction.selector === 3);
                
                if (!storageUpdateInteraction) {
                    storageUpdateInteraction = {
                        selector: 3, // Storage Updates
                        value: []
                    };
                    account.transactions.get(txIndex)!.push(storageUpdateInteraction);
                }
                
                storageUpdateInteraction.value.push({
                    key: slotChange.slot,
                    value: change.newValue
                });
            }
        }

        // Process storage reads (no txIndex, so we need to handle differently)
        if (accountChange.storageReads.length > 0) {
            // For storage reads, we don't have txIndex info in baseline
            // This is a limitation of the baseline format
            // We'll need to make assumptions or handle this differently
        }
    }

    // Convert to compact format
    const compactAccounts = Array.from(accountMap.values()).map(account => ({
        address: account.address,
        transactions: Array.from(account.transactions.entries()).map(([txIndex, interactions]) => ({
            txIndex,
            interactions
        }))
    }));

    return {
        accounts: compactAccounts
    };
}

export function compactToBaseline(compact: CompactData): BaselineData {
    const accountChangesMap = new Map<string, any>();

    for (const touchedAccount of compact.accounts) {
        const addressKey = Buffer.from(touchedAccount.address).toString('hex');
        
        if (!accountChangesMap.has(addressKey)) {
            accountChangesMap.set(addressKey, {
                address: touchedAccount.address,
                storageChanges: new Map<string, any[]>(),
                storageReads: [],
                balanceChanges: [],
                nonceChanges: [],
                codeChanges: []
            });
        }
        
        const account = accountChangesMap.get(addressKey)!;

        for (const txInteraction of touchedAccount.transactions) {
            const txIndex = txInteraction.txIndex;
            
            for (const interaction of txInteraction.interactions) {
                switch (interaction.selector) {
                    case 0: // Nonce Update
                        account.nonceChanges.push({
                            txIndex,
                            newNonce: interaction.value
                        });
                        break;
                        
                    case 1: // Balance Update
                        account.balanceChanges.push({
                            txIndex,
                            newBalance: interaction.value
                        });
                        break;
                        
                    case 2: // Code Update
                        account.codeChanges.push({
                            txIndex,
                            newCode: interaction.value
                        });
                        break;
                        
                    case 3: // Storage Updates
                        for (const storageWrite of interaction.value) {
                            const slotKey = Buffer.from(storageWrite.key).toString('hex');
                            if (!account.storageChanges.has(slotKey)) {
                                account.storageChanges.set(slotKey, []);
                            }
                            account.storageChanges.get(slotKey)!.push({
                                txIndex,
                                newValue: storageWrite.value
                            });
                        }
                        break;
                        
                    case 4: // Storage Reads
                        for (const storageKey of interaction.value) {
                            account.storageReads.push(storageKey);
                        }
                        break;
                        
                    case 5: // Account Deleted
                        // Handle account deletion if needed
                        break;
                }
            }
        }
    }

    // Convert to baseline format
    const accountChanges = Array.from(accountChangesMap.values()).map(account => ({
        address: account.address,
        storageChanges: Array.from(account.storageChanges.entries()).map(([slot, changes]) => ({
            slot: Buffer.from(slot, 'hex'),
            changes
        })),
        storageReads: account.storageReads,
        balanceChanges: account.balanceChanges,
        nonceChanges: account.nonceChanges,
        codeChanges: account.codeChanges
    }));

    return {
        accountChanges
    };
}