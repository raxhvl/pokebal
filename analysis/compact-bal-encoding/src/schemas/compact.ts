import {
    BooleanType,
    ByteListType,
    ByteVectorType,
    ContainerType,
    ListCompositeType,
    UintBigintType,
    UintNumberType,
    UnionType,
} from "@chainsafe/ssz";

const MAX_TXS = 30_000;
const MAX_SLOTS = 300_000;
const MAX_ACCOUNTS = 300_000;
const MAX_CODE_SIZE = 24_576;
const MAX_INTERACTIONS = 6;

const StorageWrite = new ContainerType({
    key: new ByteVectorType(32),
    value: new ByteVectorType(32),
});

const StorageUpdates = new ListCompositeType(StorageWrite, MAX_SLOTS);
const StorageReads = new ListCompositeType(new ByteVectorType(32), MAX_SLOTS);

const Interaction = new UnionType([
    new UintNumberType(8),      // Nonce Update
    new UintBigintType(16),     // Balance Update  
    new ByteListType(MAX_CODE_SIZE), // Code Update
    StorageUpdates,             // Storage Updates
    StorageReads,               // Storage Reads
    new BooleanType(),          // Account Deleted
]);

const TransactionInteractions = new ContainerType({
    txIndex: new UintNumberType(2),
    interactions: new ListCompositeType(Interaction, MAX_INTERACTIONS),
});

const TouchedAccount = new ContainerType({
    address: new ByteVectorType(20),
    transactions: new ListCompositeType(TransactionInteractions, MAX_TXS),
});

export const CompactBlockAccessLists = new ContainerType({
    accounts: new ListCompositeType(TouchedAccount, MAX_ACCOUNTS),
});