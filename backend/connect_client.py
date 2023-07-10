import logging
import os
from typing import Any, Dict, List

import requests


async def get_iframe_details() -> dict:
    """
    Returns the constructed URL for the iFrame, using the first available page and an authorization code.

    Returns:
        str: iFrame URL
    """
    first_available_page = (await _get_pages())[0]
    auth_code = await _get_auth_code(first_available_page["extension"]["login_uri"])

    return {
        "url": f"https://"
        f"{first_available_page['extension']['hostname']}."
        f"{first_available_page['extension']['domain']}"
        f"{first_available_page['extension']['login_uri']}?"
        f"code={auth_code}&"
        f"redirect_to="
        f"{first_available_page['url']}",
        "label": first_available_page["label"],
        "icon": "https://www.iana.org/_img/2022/iana-logo-header.svg",
    }


async def _get_pages() -> List[Dict[str, Any]]:
    """
    Fetches pages from the "/public/v1/devops/pages" endpoint of the API.

    The method calls the `_connect_api_request` method with "GET" method to fetch data.
    If the pages array is empty, it logs an error and raises an exception.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries where each dictionary represents a page.

    Raises:
        Exception: If the pages array is empty, an exception is raised with a relevant error message.
    """
    pages_array = await _connect_api_request("/public/v1/devops/pages", "GET")
    if not pages_array:
        logging.error("Error: pages request returned empty array")
        raise Exception("Error: pages request returned empty array")

    return pages_array


async def _get_auth_code(login_url: str) -> str:
    """
    Fetches the authentication code from the provided login_url endpoint of the API.

    The method calls the `_connect_api_request` method with "POST" method to fetch data.
    If the response JSON does not contain a "code", it logs an error and raises an exception.

    Args:
        login_url (str): The login URL to which the POST request will be sent.

    Returns:
        str: The authentication code retrieved from the response JSON.

    Raises:
        Exception: If the "code" is not found in the response JSON,
        an exception is raised with a relevant error message.
    """
    response_json = await _connect_api_request(login_url, "POST")

    if "code" not in response_json:
        logging.error('Error: "code" not in response JSON')
        raise Exception('Error: "code" not in response JSON')

    return response_json.get("code")


async def _connect_api_request(endpoint: str, method: str) -> Any:
    """
    Makes an API request to the provided endpoint using the specified HTTP method.

    The function constructs the URL and headers,
    and then sends either a GET or POST request based on the `method` parameter. If `with_impersonation` is set to True,
    an additional header 'Impersonation' is added. If the response indicates an HTTP error or other request error,
    this function logs the error and re-raises the exception.
    If the request is successful, it returns the JSON response.

    Args:
        endpoint (str): The API endpoint to be accessed.
        method (str): The HTTP method to use for the request ("GET" or "POST").
        with_impersonation (bool, optional): Whether to include the 'Impersonation' header. Defaults to False.

    Returns:
        Any: The JSON response from the API request. dict or array

    Raises:
        requests.exceptions.HTTPError: If an HTTP error occurs.
        requests.exceptions.RequestException: If a request error occurs.
    """
    tier_account_id = os.getenv("TIER_ACCOUNT_ID")
    api_host = os.getenv("API_HOST")
    api_key = os.getenv("API_KEY")

    if not all([api_host, tier_account_id, api_key]):
        raise Exception("Required environment variables are not set")

    url = f"https://{api_host}{endpoint}"
    headers = {"Authorization": api_key, "Impersonation": tier_account_id}

    try:
        if method == "POST":
            response = requests.post(url, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        raise

    return response.json()
