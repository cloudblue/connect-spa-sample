import logging
import re
from typing import Any, Dict

from connect.client import AsyncConnectClient


class Client:
    def __init__(self, tier_account_id, api_host, api_key):
        self.connect_client = AsyncConnectClient(
            api_key=api_key,
            endpoint=api_host,
            default_headers={"Impersonation": tier_account_id},
        )

    async def get_iframe_details(self) -> dict:
        """
        Returns the constructed URL for the iFrame, using the first available page and an authorization code.

        Returns:
            str: iFrame URL
        """
        first_available_page = await self._get_first_page()
        auth_code = await self._get_auth_code(
            first_available_page["extension"]["login_uri"]
        )

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

    async def _get_first_page(self) -> Dict[str, Any]:
        """
        Fetches the first page from the "/public/v1/devops/pages" endpoint of the API.
        If the pages array is empty, it logs an error and raises an exception.

        Returns:
            Dict[str, Any]: A dictionary represents a page.

        Raises:
            Exception: If the pages array is empty, an exception is raised with a relevant error message.
        """
        page = await self.connect_client("devops").collection("pages").filter(integration_point='customer').first()

        if not page:
            logging.error("Error: pages request returned empty array")
            raise Exception("Error: pages request returned empty array")

        return page

    async def _get_auth_code(self, login_url: str) -> str:
        """
        Fetches the authentication code from the provided login_url endpoint of the API.

        If the response JSON does not contain a "code", it logs an error and raises an exception.

        Args:
            login_url (str): The login URL to which the POST request will be sent.

        Returns:
            str: The authentication code retrieved from the response JSON.

        Raises:
            Exception: If the "code" is not found in the response JSON,
            an exception is raised with a relevant error message.
        """
        ext_id = re.search(r"EXT-\d+-\d+", login_url)
        if not ext_id:
            raise Exception("EXT-id not found in login_url")

        response_json = (
            await self.connect_client("auth").eaas[ext_id.group()]("login").post()
        )

        if "code" not in response_json:
            logging.error('Error: "code" not in response JSON')
            raise Exception('Error: "code" not in response JSON')

        return response_json.get("code")
