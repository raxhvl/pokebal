import {
    ByteListType,
    ByteVectorType,
    ContainerType,
    ListCompositeType,
    UintBigintType,
    UintNumberType,
} from "@chainsafe/ssz";

const MAX_TXS = 30_000;
const MAX_SLOTS = 300_000;
const MAX_ACCOUNTS = 300_000;
const MAX_CODE_SIZE = 24_576;

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

export const BaselineBlockAccessLists = new ContainerType({
    accountChanges: new ListCompositeType(AccountChanges, MAX_ACCOUNTS),
});