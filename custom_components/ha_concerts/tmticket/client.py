"""API client classes"""
import aiohttp
import asyncio
import logging
from collections import namedtuple
from urllib import parse
from ticketpy.query import AttractionQuery, ClassificationQuery, EventQuery, VenueQuery
from ticketpy.model import Page

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(sf)
log.addHandler(sh)


class AsyncApiClient:
    """AsyncApiClient is the main wrapper for the Discovery API, updated for asynchronous operation.
    
    Example:    
    Get the first page result for venues matching keyword 'Tabernacle':
    
    ```
    import ticketpy
    import asyncio
    
    async def main():
        client = ticketpy.AsyncApiClient("your_api_key")
        resp = await client.venues.find(keyword="Tabernacle").one()
        for venue in resp:
            print(venue.name)
    if __name__ == "__main__":
        asyncio.run(main())
    ```
    """
    root_url = 'https://app.ticketmaster.com'
    url = 'https://app.ticketmaster.com/discovery/v2'

    def __init__(self, api_key):
        self.__api_key = None
        self.api_key = api_key
        self.events = EventQuery(api_client=self)
        self.venues = VenueQuery(api_client=self)
        self.attractions = AttractionQuery(api_client=self)
        self.classifications = ClassificationQuery(api_client=self)
        self.segment_by_id = self.classifications.segment_by_id
        self.genre_by_id = self.classifications.genre_by_id
        self.subgenre_by_id = self.classifications.subgenre_by_id

    async def search(self, method, **kwargs):
        """Generic API request, converted for asynchronous operation"""
        kwargs = {k: v for (k, v) in kwargs.items() if v is not None}
        updates = self.api_key

        for k, v in kwargs.items():
            if k in ['includeTBA', 'includeTBD', 'includeTest']:
                updates[k] = self.__yes_no_only(v)
            elif k in ['size', 'radius', 'marketId']:
                updates[k] = str(v)
        kwargs.update(updates)

        urls = {
            'events': self.__method_url('events'),
            'venues': self.__method_url('venues'),
            'attractions': self.__method_url('attractions'),
            'classifications': self.__method_url('classifications')
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(urls[method], params=kwargs) as resp:
                return await self._handle_response(resp)

    async def _handle_response(self, response):
        """Handles response, raising ApiException if needed or returning response JSON object asynchronously"""
        if response.status == 200:
            return await response.json()
        elif response.status == 401:
            self.__fault(await response.json())
        elif response.status == 400:
            self.__error(await response.json())
        else:
            self.__unknown_error(await response.json())

    async def get_url(self, link):
        """Gets a specific href from '_links' object in a response, asynchronously"""
        parsed_link = self._parse_link(link)
        async with aiohttp.ClientSession() as session:
            async with session.get(parsed_link.url, params=parsed_link.params) as resp:
                return Page.from_json(await self._handle_response(resp))

    @property
    def api_key(self):
        return self.__api_key

    @api_key.setter
    def api_key(self, api_key):
        self.__api_key = {'apikey': api_key}

    @staticmethod
    def __method_url(method):
        return "{}/{}.json".format(AsyncApiClient.url, method)

    @staticmethod
    def __yes_no_only(s):
        s = str(s).lower()
        if s in ['true', 'yes']:
            s = 'yes'
        elif s in ['false', 'no']:
            s = 'no'
        return s


class ApiException(Exception):
    """Exception thrown for API-related error messages"""
    def __init__(self, *args):
        super().__init__(*args)

class AsyncPagedResponse:
    """Asynchronously iterates through API response pages."""
    def __init__(self, api_client, response):
        self.api_client = api_client
        self.page = None
        self.page = Page.from_json(response)

    async def limit(self, max_pages=5):
        """Asynchronously retrieve a number of pages, returning a list of all entities."""
        all_items = []
        counter = 0
        async for pg in self:
            if counter >= max_pages:
                break
            counter += 1
            all_items.extend(pg)
        return all_items

    async def one(self):
        """Asynchronously get items from the first page result."""
        return [i for i in self.page]

    async def maximum(self, max_pages=49): # API limits paging depth to (page * size) <= 1000
        """Asynchronously retrieves maximum pages in a result, returning a flat list."""
        all_items = []
        counter = 0
        async for pg in self:
            if counter >= max_pages:
                break
            counter += 1
            all_items.extend(pg)
        return all_items

    def __aiter__(self):
        return self._page_iterator()

    async def _page_iterator(self):
        current_page = self.page
        yield current_page
        next_url = current_page.links.get('next')
        
        while next_url:
            log.debug(f"Requesting page: {next_url}")
            page_data = await self.api_client.get_url(next_url)
            current_page = Page.from_json(page_data)
            next_url = current_page.links.get('next')
            yield current_page
