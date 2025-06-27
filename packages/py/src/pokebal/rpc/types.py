from typing import Dict, List, Optional
from pydantic import BaseModel

from pokebal.common.types import (
    HexString,
    Address,
    Hash,
)


class AccountState(BaseModel):
    """Account state information."""

    balance: Optional[HexString] = None
    code: Optional[HexString] = None
    nonce: Optional[int] = None
    storage: Optional[Dict[HexString, HexString]] = None


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
