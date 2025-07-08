from typing import Dict, List, Optional
from pydantic import BaseModel

# Type aliases for bytes
Address = bytes
Hash = bytes


class AccountState(BaseModel):
    """Account state information."""

    balance: Optional[bytes] = None
    code: Optional[bytes] = None
    nonce: Optional[int] = None
    storage: Optional[Dict[bytes, bytes]] = None


class PrePostStates(BaseModel):
    """Pre and post states for debug trace result."""

    pre: Dict[Address, AccountState]
    post: Dict[Address, AccountState]


class TransactionTrace(BaseModel):
    """Individual transaction trace."""

    result: PrePostStates
    txHash: Hash


# Type aliases for common RPC types
BlockDebugTraceResult = List[TransactionTrace]
