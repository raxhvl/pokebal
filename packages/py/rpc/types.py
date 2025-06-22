from typing import Dict, List, Literal, Union, Optional, Annotated
from pydantic import BaseModel, Field


# Base hex string validation
HexString = Annotated[str, Field(pattern=r"^0x[0-9a-fA-F]+$")]

# Specific hex string types that extend the base pattern
Address = Annotated[
    HexString,
    Field(pattern=r"^0x[0-9a-fA-F]{40}$", description="Ethereum address (20 bytes)"),
]
Hash = Annotated[
    HexString, Field(pattern=r"^0x[0-9a-fA-F]{64}$", description="Hash (32 bytes)")
]


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
BlockNumber = Union[int, Literal["latest", "earliest", "pending"]]

BlockDebugTraceResult = List[TransactionTrace]
