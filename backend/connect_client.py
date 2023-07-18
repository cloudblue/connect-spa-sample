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
            first_available_page["extension"]["extension_id"]
        )

        extension_full_url = (
            f"https://{first_available_page['extension']['hostname']}."
            f"{first_available_page['extension']['domain']}"
        )
        login_url = (
            f"{extension_full_url}{first_available_page['extension']['login_uri']}?"
            f"code={auth_code}&redirect_to={first_available_page['url']}"
        )
        icon_url = f"{extension_full_url}{first_available_page['icon']}"

        return {
            "url": login_url,
            "label": first_available_page["label"],
            "icon": icon_url,
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
        page = (
            await self.connect_client("devops")
            .collection("pages")
            .filter(integration_point="customer")
            .first()
        )

        if not page:
            logging.error("Error: pages request returned empty array")
            raise Exception("Error: pages request returned empty array")

        return page

    async def _get_auth_code(self, extension_id: str) -> str:
        """
        Fetches the authentication code from the login endpoint of the API.

        If the response JSON does not contain a "code", it logs an error and raises an exception.

        Args:
            extension_id (str): Extension id to be called upon. (EXT-000-000)

        Returns:
            str: The authentication code retrieved from the response JSON.

        Raises:
            Exception: If the "code" is not found in the response JSON,
            an exception is raised with a relevant error message.
        """

        response_json = (
            await self.connect_client("auth").eaas[extension_id]("login").post()
        )

        if "code" not in response_json:
            logging.error('Error: "code" not in response JSON')
            raise Exception('Error: "code" not in response JSON')

        return response_json.get("code")
