"""Tests for balance change utility functions."""

import pytest
from bal.utils import (
    is_valid_balance_delta,
    encode_balance_delta,
    create_balance_change_entry
)



class TestIsValidBalanceDelta:
    """Test balance delta validation."""
    
    def test_valid_positive_delta(self):
        """Test valid positive delta."""
        delta = 1_000_000
        assert is_valid_balance_delta(delta) is True
    
    def test_valid_negative_delta(self):
        """Test valid negative delta."""
        delta = -1_000_000
        assert is_valid_balance_delta(delta) is True
    
    def test_valid_zero_delta(self):
        """Test zero delta."""
        assert is_valid_balance_delta(0) is True
    
    def test_max_positive_value(self):
        """Test maximum valid positive value (2^95 - 1)."""
        max_val = 2**95 - 1
        assert is_valid_balance_delta(max_val) is True
    
    def test_max_negative_value(self):
        """Test maximum valid negative value (-2^95)."""
        min_val = -(2**95)
        assert is_valid_balance_delta(min_val) is True
    
    def test_exceeds_positive_limit(self):
        """Test value exceeding positive limit."""
        over_limit = 2**95
        assert is_valid_balance_delta(over_limit) is False
    
    def test_exceeds_negative_limit(self):
        """Test value exceeding negative limit."""
        under_limit = -(2**95) - 1
        assert is_valid_balance_delta(under_limit) is False


class TestEncodeBalanceDelta:
    """Test balance delta encoding."""
    
    def test_encode_positive_delta(self):
        """Test encoding positive delta."""
        delta = 100
        result = encode_balance_delta(delta)
        assert result.startswith('0x')
        assert len(result) == 26  # 0x + 24 hex chars (12 bytes)
        assert result == '0x000000000000000000000064'
    
    def test_encode_negative_delta(self):
        """Test encoding negative delta using two's complement."""
        delta = -100
        result = encode_balance_delta(delta)
        assert result.startswith('0x')
        assert len(result) == 26
        # Two's complement of -100 in 12 bytes
        assert result == '0xffffffffffffffffffffff9c'
    
    def test_encode_zero_delta(self):
        """Test encoding zero delta."""
        result = encode_balance_delta(0)
        assert result == '0x000000000000000000000000'
    
    def test_encode_large_positive(self):
        """Test encoding large positive value."""
        delta = 1_000_000_000_000_000_000  # 1 ETH in wei
        result = encode_balance_delta(delta)
        assert result.startswith('0x')
        assert len(result) == 26
    
    def test_encode_max_positive(self):
        """Test encoding maximum positive value."""
        delta = 2**95 - 1
        result = encode_balance_delta(delta)
        assert result.startswith('0x')
        assert result == '0x7fffffffffffffffffffffff'
    
    def test_encode_max_negative(self):
        """Test encoding maximum negative value."""
        delta = -(2**95)
        result = encode_balance_delta(delta)
        assert result.startswith('0x')
        assert result == '0x800000000000000000000000'
    
    def test_encode_invalid_positive_delta(self):
        """Test encoding delta that exceeds positive limit."""
        delta = 2**95
        with pytest.raises(ValueError, match="exceeds 12-byte two's complement range"):
            encode_balance_delta(delta)
    
    def test_encode_invalid_negative_delta(self):
        """Test encoding delta that exceeds negative limit."""
        delta = -(2**95) - 1
        with pytest.raises(ValueError, match="exceeds 12-byte two's complement range"):
            encode_balance_delta(delta)


class TestCreateBalanceChangeEntry:
    """Test balance change entry creation."""
    
    def test_create_positive_change(self):
        """Test creating entry for positive balance change."""
        result = create_balance_change_entry(5, 100)
        assert result.tx_index == 5
        assert result.delta == '0x000000000000000000000064'
    
    def test_create_negative_change(self):
        """Test creating entry for negative balance change."""
        result = create_balance_change_entry(3, -100)
        assert result.tx_index == 3
        assert result.delta == '0xffffffffffffffffffffff9c'
    
    def test_create_zero_change_returns_none(self):
        """Test that zero delta returns None."""
        result = create_balance_change_entry(1, 0)
        assert result is None
    
    def test_create_large_change(self):
        """Test creating entry for large balance change."""
        delta = 1_000_000_000_000_000_000  # 1 ETH
        result = create_balance_change_entry(10, delta)
        assert result is not None
        assert result.tx_index == 10
        assert result.delta.startswith('0x')
        assert len(result.delta) == 26
    
    def test_create_invalid_change_raises_error(self):
        """Test that invalid delta raises ValueError."""
        invalid_delta = 2**95
        with pytest.raises(ValueError):
            create_balance_change_entry(1, invalid_delta)