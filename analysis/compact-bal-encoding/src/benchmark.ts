import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import { BaselineBlockAccessLists } from './schemas/baseline';

const baselineDir = './src/data/baseline';

function analyzeTransactionAccessCoverage(baselineBALs: any[]) {
    const fieldCoverage = {
        1: 0, // Only 1 field touched
        2: 0, // 2 fields touched  
        3: 0, // 3 fields touched
        4: 0  // All 4 fields touched
    };
    
    let totalTransactions = 0;
    
    for (const bal of baselineBALs) {
        for (const account of bal.accountChanges) {
            const txFields = new Map<number, Set<string>>();
            
            // Track storage changes
            for (const slotChange of account.storageChanges) {
                for (const change of slotChange.changes) {
                    if (!txFields.has(change.txIndex)) {
                        txFields.set(change.txIndex, new Set());
                    }
                    txFields.get(change.txIndex)!.add('storage');
                }
            }
            
            // Track balance changes
            for (const balanceChange of account.balanceChanges) {
                if (!txFields.has(balanceChange.txIndex)) {
                    txFields.set(balanceChange.txIndex, new Set());
                }
                txFields.get(balanceChange.txIndex)!.add('balance');
            }
            
            // Track nonce changes
            for (const nonceChange of account.nonceChanges) {
                if (!txFields.has(nonceChange.txIndex)) {
                    txFields.set(nonceChange.txIndex, new Set());
                }
                txFields.get(nonceChange.txIndex)!.add('nonce');
            }
            
            // Track code changes
            for (const codeChange of account.codeChanges) {
                if (!txFields.has(codeChange.txIndex)) {
                    txFields.set(codeChange.txIndex, new Set());
                }
                txFields.get(codeChange.txIndex)!.add('code');
            }
            
            // Count fields touched per transaction
            for (const [txIndex, fields] of txFields) {
                totalTransactions++;
                const fieldCount = fields.size;
                if (fieldCount <= 4) {
                    fieldCoverage[fieldCount as keyof typeof fieldCoverage]++;
                }
            }
        }
    }
    
    console.log('\n=== Transaction Access Coverage Analysis ===');
    console.log(`Total transactions analyzed: ${totalTransactions}`);
    console.log('\nFields touched in header | Share of transactions');
    console.log('------------------------ | ---------------------');
    
    for (let i = 1; i <= 4; i++) {
        const count = fieldCoverage[i as keyof typeof fieldCoverage];
        const percentage = totalTransactions > 0 ? ((count / totalTransactions) * 100).toFixed(1) : '0.0';
        const fieldLabel = i === 4 ? 'All 4 fields' : `${i} field${i > 1 ? 's' : ''}`;
        console.log(`${fieldLabel.padEnd(24)} | **${percentage} %**`);
    }
}


try {
    const files = readdirSync(baselineDir).filter(file => file.endsWith('.ssz'));
    console.log(`Found ${files.length} SSZ files in baseline folder`);

    const baselineBALs = []
    
    for (const file of files) {
        const filePath = join(baselineDir, file);
        console.log(`\nProcessing: ${file}`);
        
        try {
            const ssz = readFileSync(filePath);
            console.log(`  Loaded ${ssz.length} bytes`);
            baselineBALs.push(BaselineBlockAccessLists.deserialize(ssz))
            
        } catch (error) {
            console.error(`  Error decoding ${file}:`, error);
        }
    }

    analyzeTransactionAccessCoverage(baselineBALs)
    
} catch (error) {
    console.error('Error reading baseline directory:', error);
}