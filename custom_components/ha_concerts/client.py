import aiohttp
import asyncio

class TicketmasterAPI:
    def __init__(self, api_key, session=None):
        self.api_key = api_key
        self.base_url = "https://app.ticketmaster.com/discovery/v2/"
        self.session = session or aiohttp.ClientSession()

    async def _get(self, endpoint, **kwargs):
        """Internal method to handle GET requests asynchronously."""
        params = kwargs
        params['apikey'] = self.api_key
        try:
            async with self.session.get(f"{self.base_url}{endpoint}", params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            print(f"Client error occurred: {err}")
        except asyncio.TimeoutError as err:
            print(f"Timeout error occurred: {err}")

    async def get_events(self, keyword="", country_code="", size=10, page=0):
        """Asynchronously search for events."""
        return await self._get("events.json", keyword=keyword, countryCode=country_code, size=size, page=page)

    async def get_event_details(self, event_id):
        """Asynchronously get details for a specific event by ID."""
        return await self._get(f"events/{event_id}.json")

    async def get_venue_details(self, venue_id):
        """Asynchronously get details for a specific venue by ID."""
        return await self._get(f"venues/{venue_id}.json")

    async def search_venues(self, lat=None, long=None, keyword="", size=10, page=0):
        """
        Asynchronously search for venues by GPS coordinates and/or keyword.
        :param lat: Latitude for the venue search.
        :param long: Longitude for the venue search.
        :param keyword: Search term for venues.
        :param size: Number of venues to return.
        :param page: Page number for pagination.
        :return: JSON response containing venues.
        """
        params = {}
        if lat and long:
            params['geoPoint'] = f"{lat},{long}"
        if keyword:
            params['keyword'] = keyword
        params['size'] = size
        params['page'] = page
        return await self._get("venues.json", **params)
