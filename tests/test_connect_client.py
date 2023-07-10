import os
from unittest.mock import AsyncMock, patch

import pytest
from requests.exceptions import HTTPError, RequestException
from requests.models import Response

import backend.connect_client as connect_client


@pytest.mark.asyncio
async def test_get_iframe_url_success():
    mock_pages = [
        {
            "extension": {
                "login_uri": "/test_login_uri",
                "hostname": "test_host",
                "domain": "test_domain",
            },
            "url": "/test_url",
            "label": "test label",
        }
    ]
    mock_code = "test_code"

    with patch.object(
        connect_client,
        "_get_pages",
        return_value=mock_pages,
        new_callable=AsyncMock,
    ), patch.object(
        connect_client,
        "_get_auth_code",
        return_value=mock_code,
        new_callable=AsyncMock,
    ):
        result = await connect_client.get_iframe_details()

        assert result == {
            "url": "https://test_host.test_domain/test_login_uri?code=test_code&redirect_to=/test_url",
            "icon": "https://www.iana.org/_img/2022/iana-logo-header.svg",
            "label": "test label",
        }


@pytest.mark.asyncio
async def test_get_iframe_url_empty_pages():
    mock_pages = []

    with patch.object(
        connect_client,
        "_connect_api_request",
        return_value=mock_pages,
        new_callable=AsyncMock,
    ):
        with pytest.raises(
            Exception, match="Error: pages request returned empty array"
        ):
            await connect_client.get_iframe_details()


@pytest.mark.asyncio
async def test_get_iframe_url_no_auth_code():
    mock_pages = [
        {
            "extension": {
                "login_uri": "/test_login_uri",
                "hostname": "test_host",
                "domain": "test_domain",
            },
            "url": "/test_url",
        }
    ]

    with patch.object(
        connect_client,
        "_get_pages",
        return_value=mock_pages,
        new_callable=AsyncMock,
    ), patch.object(
        connect_client,
        "_get_auth_code",
        side_effect=Exception('Error: "code" not in response JSON'),
        new_callable=AsyncMock,
    ):
        with pytest.raises(Exception, match='Error: "code" not in response JSON'):
            await connect_client.get_iframe_details()


@pytest.fixture(autouse=True)
def env_setup():
    """
    Setup and teardown for environment variables.
    """
    os.environ["TIER_ACCOUNT_ID"] = "test_tier_account_id"
    os.environ["API_HOST"] = "test_api_host"
    os.environ["API_KEY"] = "test_api_key"
    yield
    if "TIER_ACCOUNT_ID" in os.environ:
        os.environ.pop("TIER_ACCOUNT_ID")
    if "API_HOST" in os.environ:
        os.environ.pop("API_HOST")
    if "API_KEY" in os.environ:
        os.environ.pop("API_KEY")


@patch("backend.connect_client._connect_api_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_pages_valid_pages(mock_connect):
    # Mocking the _connect_api_request method to return a list of pages
    mock_connect.return_value = [{"page1": "data"}, {"page2": "data"}]

    result = await connect_client._get_pages()

    assert result == [{"page1": "data"}, {"page2": "data"}]
    mock_connect.assert_called_once_with("/public/v1/devops/pages", "GET")


@patch("backend.connect_client._connect_api_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_pages_empty_list(mock_connect):
    # Mocking the _connect_api_request method to return an empty list
    mock_connect.return_value = []

    with pytest.raises(Exception) as e:
        await connect_client._get_pages()

    assert str(e.value) == "Error: pages request returned empty array"


@patch("backend.connect_client._connect_api_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_pages_http_error(mock_connect):
    # Mocking the _connect_api_request method to raise an HTTPError
    mock_connect.side_effect = HTTPError()

    with pytest.raises(HTTPError):
        await connect_client._get_pages()


@patch("backend.connect_client._connect_api_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_pages_request_exception(mock_connect):
    # Mocking the _connect_api_request method to raise a RequestException
    mock_connect.side_effect = RequestException()

    with pytest.raises(RequestException):
        await connect_client._get_pages()


@pytest.mark.asyncio
async def test_get_pages_env_vars_not_set():
    # Remove the environment variables for this test
    os.environ.pop("TIER_ACCOUNT_ID")
    os.environ.pop("API_HOST")
    os.environ.pop("API_KEY")

    with pytest.raises(Exception) as e:
        await connect_client._get_pages()

    assert str(e.value) == "Required environment variables are not set"


@patch("backend.connect_client._connect_api_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_auth_code_valid_response(mock_connect):
    mock_connect.return_value = {"code": "1234"}

    response = await connect_client._get_auth_code("test_login_url")

    assert response == "1234"
    mock_connect.assert_called_once_with("test_login_url", "POST")


@patch("backend.connect_client._connect_api_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_auth_code_response_without_code(mock_connect):
    mock_connect.return_value = {"something_else": "1234"}
    with pytest.raises(Exception, match='Error: "code" not in response JSON'):
        await connect_client._get_auth_code("test_login_url")


@patch("backend.connect_client._connect_api_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_auth_code_http_error(mock_connect):
    mock_connect.side_effect = HTTPError()

    with pytest.raises(HTTPError):
        await connect_client._get_auth_code("test_login_url")


@patch("backend.connect_client._connect_api_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_auth_code_request_exception(mock_connect):
    mock_connect.side_effect = RequestException()

    with pytest.raises(RequestException):
        await connect_client._get_auth_code("test_login_url")


@pytest.mark.asyncio
async def test_get_auth_code_env_vars_not_set():
    os.environ.pop("TIER_ACCOUNT_ID", None)
    os.environ.pop("API_HOST", None)
    os.environ.pop("API_KEY", None)

    with pytest.raises(Exception, match="Required environment variables are not set"):
        await connect_client._get_auth_code("test_login_url")


@pytest.mark.asyncio
@patch("requests.get")
async def test_connect_api_request_get_with_impersonation(mock_get):
    mock_get.return_value.json.return_value = {"key": "value"}

    response = await connect_client._connect_api_request("/test_endpoint", "GET")

    mock_get.assert_called_once_with(
        "https://test_api_host/test_endpoint",
        headers={
            "Authorization": "test_api_key",
            "Impersonation": "test_tier_account_id",
        },
    )
    assert response == {"key": "value"}


@pytest.mark.asyncio
@patch("requests.post")
async def test_connect_api_request_post_with_impersonation(mock_post):
    mock_post.return_value.json.return_value = {"key": "value"}

    response = await connect_client._connect_api_request("/test_endpoint", "POST")

    mock_post.assert_called_once_with(
        "https://test_api_host/test_endpoint",
        headers={
            "Authorization": "test_api_key",
            "Impersonation": "test_tier_account_id",
        },
    )
    assert response == {"key": "value"}


@pytest.mark.asyncio
@patch("requests.get")
async def test_connect_api_request_get_http_error(mock_get):
    mock_response = Response()
    mock_response.status_code = 500

    mock_get.return_value.raise_for_status.side_effect = HTTPError(
        response=mock_response
    )
    with pytest.raises(HTTPError):
        await connect_client._connect_api_request("/test_endpoint", "GET")


@pytest.mark.asyncio
@patch("requests.get")
async def test_connect_api_request_get_request_exception(mock_get):
    mock_get.side_effect = RequestException

    with pytest.raises(RequestException):
        await connect_client._connect_api_request("/test_endpoint", "GET")
