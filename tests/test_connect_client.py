import os
from unittest.mock import AsyncMock, patch

import pytest
from connect.client.testing import AsyncConnectClientMocker

import backend.connect_client as connect_client


@pytest.mark.asyncio
async def test_get_iframe_url_success():
    mock_pages = {
        "extension": {
            "login_uri": "/test_login_uri",
            "hostname": "test_host",
            "domain": "test_domain",
        },
        "url": "/test_url",
        "label": "test label",
    }
    mock_code = "test_code"

    with patch.object(
        connect_client.Client,
        "_get_first_page",
        return_value=mock_pages,
        new_callable=AsyncMock,
    ), patch.object(
        connect_client.Client,
        "_get_auth_code",
        return_value=mock_code,
        new_callable=AsyncMock,
    ):
        client = connect_client.Client(
            api_key=os.getenv("API_KEY"),
            api_host=os.getenv("API_HOST"),
            tier_account_id=os.getenv("TIER_ACCOUNT_ID"),
        )

        result = await client.get_iframe_details()

        assert result == {
            "url": "https://test_host.test_domain/test_login_uri?code=test_code&redirect_to=/test_url",
            "icon": "https://www.iana.org/_img/2022/iana-logo-header.svg",
            "label": "test label",
        }
