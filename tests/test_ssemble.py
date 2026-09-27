"""Unit tests for Ssemble Client and Cloud Bridge."""

import pytest
from unittest.mock import MagicMock, patch
from src.core.ssemble_client import SsembleClient, SsembleAPIError
from src.modules.assembly.ssemble_bridge import SsembleBridge


def test_ssemble_client_init_and_missing_key():
    client = SsembleClient(api_key="")
    with pytest.raises(SsembleAPIError, match="SSEMBLE_API_KEY is not set"):
        _ = client.headers


def test_ssemble_client_payload_validation():
    client = SsembleClient(api_key="test_key_abc123")
    with pytest.raises(ValueError, match="Must provide either a YouTube 'url' or a direct 'file_url'"):
        client.create_short()


def test_ssemble_bridge_cloudflared_detection():
    bridge = SsembleBridge(ssemble_client=SsembleClient(api_key="mock_key"))
    cf_path = bridge._get_cloudflared_path()
    # Since we have downloaded cloudflared into assets/bin/, this should be found
    assert cf_path is not None
    assert "cloudflared" in cf_path.lower()
