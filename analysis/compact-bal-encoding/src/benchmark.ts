import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import { BaselineBlockAccessLists } from './schemas/baseline';
import { CompactBlockAccessLists } from './schemas/compact';
import { baselineToCompact } from './adapter';
import { compressSync } from 'snappy';

const baselineDir = './src/data/baseline';

function bytesToKiB(bytes: number): number {
    return bytes / 1024;
}

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

function analyzeSize(baselineBALs: any[]) {
    console.log('\n=== Size Analysis ===');
    
    const baselineSizes: number[] = [];
    const compactSizes: number[] = [];
    const baselineCompressedSizes: number[] = [];
    const compactCompressedSizes: number[] = [];
    
    for (const baselineBAL of baselineBALs) {
        // Calculate baseline size
        const baselineSerialized = BaselineBlockAccessLists.serialize(baselineBAL);
        const baselineSize = baselineSerialized.length;
        baselineSizes.push(baselineSize);
        
        // Calculate baseline compressed size
        const baselineCompressed = compressSync(baselineSerialized);
        baselineCompressedSizes.push(baselineCompressed.length);
        
        // Convert to compact and calculate size
        const compactBAL = baselineToCompact(baselineBAL);
        const compactSerialized = CompactBlockAccessLists.serialize(compactBAL);
        const compactSize = compactSerialized.length;
        compactSizes.push(compactSize);
        
        // Calculate compact compressed size
        const compactCompressed = compressSync(compactSerialized);  
        compactCompressedSizes.push(compactCompressed.length);
    }
    
    // Calculate statistics
    const baselineAvg = baselineSizes.reduce((a, b) => a + b, 0) / baselineSizes.length;
    const compactAvg = compactSizes.reduce((a, b) => a + b, 0) / compactSizes.length;
    const baselineCompressedAvg = baselineCompressedSizes.reduce((a, b) => a + b, 0) / baselineCompressedSizes.length;
    const compactCompressedAvg = compactCompressedSizes.reduce((a, b) => a + b, 0) / compactCompressedSizes.length;
    
    const savings = ((baselineAvg - compactAvg) / baselineAvg) * 100;
    const compressedSavings = ((baselineCompressedAvg - compactCompressedAvg) / baselineCompressedAvg) * 100;
    
    // Sort for percentiles
    const sortedBaseline = [...baselineSizes].sort((a, b) => a - b);
    const sortedCompact = [...compactSizes].sort((a, b) => a - b);
    
    const getPercentile = (arr: number[], p: number) => {
        const index = Math.ceil((p / 100) * arr.length) - 1;
        return arr[index];
    };
    
    console.log('\n### Average Size');
    console.log('| **Baseline** | **Baseline (🗜️Compressed)** | **Compact** | **Compact (🗜️Compressed)** | **% Savings (Compressed)** |');
    console.log('| :----------: | :---------------------------: | :---------: | :-------------------------: | :-------------------------: |');
    console.log(`| ${bytesToKiB(baselineAvg).toFixed(2)} KiB | ${bytesToKiB(baselineCompressedAvg).toFixed(2)} KiB | ${bytesToKiB(compactAvg).toFixed(2)} KiB | ${bytesToKiB(compactCompressedAvg).toFixed(2)} KiB | **${compressedSavings.toFixed(1)}%** |`);
    
    console.log('\n### Size Distribution');
    console.log('|   **Format**  | **Min (KiB)** | **P25 (KiB)** | **Median (KiB)** | **P75 (KiB)** | **Max (KiB)** |');
    console.log('| :-----------: | :-----------: | :-----------: | :--------------: | :-----------: | :-----------: |');
    
    const baselineStats = {
        min: bytesToKiB(Math.min(...sortedBaseline)),
        p25: bytesToKiB(getPercentile(sortedBaseline, 25)),
        median: bytesToKiB(getPercentile(sortedBaseline, 50)),
        p75: bytesToKiB(getPercentile(sortedBaseline, 75)),
        max: bytesToKiB(Math.max(...sortedBaseline))
    };
    
    const compactStats = {
        min: bytesToKiB(Math.min(...sortedCompact)),
        p25: bytesToKiB(getPercentile(sortedCompact, 25)),
        median: bytesToKiB(getPercentile(sortedCompact, 50)),
        p75: bytesToKiB(getPercentile(sortedCompact, 75)),
        max: bytesToKiB(Math.max(...sortedCompact))
    };
    
    console.log(`|  **Baseline** | ${baselineStats.min.toFixed(2)} | ${baselineStats.p25.toFixed(2)} | ${baselineStats.median.toFixed(2)} | ${baselineStats.p75.toFixed(2)} | ${baselineStats.max.toFixed(2)} |`);
    console.log(`|  **Compact**  | ${compactStats.min.toFixed(2)} | ${compactStats.p25.toFixed(2)} | ${compactStats.median.toFixed(2)} | ${compactStats.p75.toFixed(2)} | ${compactStats.max.toFixed(2)} |`);
    
    console.log('\n### Compression Efficiency');
    console.log('|     **Version**     | **Uncompressed (KiB)** | **Compressed (🗜️) (KiB)** | **Compression Efficiency (%)** |');
    console.log('| :-----------------: | :--------------------: | :-----------------------: | :----------------------------: |');
    const baselineCompressionEff = ((baselineAvg - baselineCompressedAvg) / baselineAvg) * 100;
    const compactCompressionEff = ((compactAvg - compactCompressedAvg) / compactAvg) * 100;
    console.log(`|     **Baseline**    | ${bytesToKiB(baselineAvg).toFixed(2)} | ${bytesToKiB(baselineCompressedAvg).toFixed(2)} | ${baselineCompressionEff.toFixed(1)}% |`);
    console.log(`|     **Compact**     | ${bytesToKiB(compactAvg).toFixed(2)} | ${bytesToKiB(compactCompressedAvg).toFixed(2)} | ${compactCompressionEff.toFixed(1)}% |`);
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
    analyzeSize(baselineBALs)
    
} catch (error) {
    console.error('Error reading baseline directory:', error);
}