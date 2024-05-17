import asyncio
import unittest
from unittest.mock import MagicMock, patch

from API_Twitter import start_API_Twitter


class TestStartAPITwitter(unittest.TestCase):

    async def mock_get_response_content(self):
        return "mocked_response_content"

    @patch('http_utility.HttpRequester.get_response_content', new_callable=MagicMock)
    async def test_happy_path(self, mock_get_response_content):
        mock_get_response_content.return_value = asyncio.Future()
        mock_get_response_content.return_value.set_result(
            "mocked_response_content")

        url = "http://127.0.0.0.1"
        twitter_api = start_API_Twitter(url)
        response = await twitter_api.get_response()

        self.assertEqual(response, ("mocked_response_content", {}))

    @patch('http_utility.HttpRequester.get_response_content', new_callable=MagicMock)
    async def test_invalid_url(self, mock_get_response_content):
        mock_get_response_content.return_value = asyncio.Future()
        mock_get_response_content.return_value.set_exception(ValueError)

        url = "invalid_url"
        twitter_api = start_API_Twitter(url)
        response = await twitter_api.get_response()

        self.assertIsNone(response)


if __name__ == '__main__':
    asyncio.run(unittest.main())
