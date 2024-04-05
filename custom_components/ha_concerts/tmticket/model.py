"""Models for API objects"""
from datetime import datetime
import re
import aiohttp  # Assuming aiohttp is used for async operations

def _assign_links(obj, json_obj, base_url=None):
    """Assigns `links` attribute to an object from JSON"""
    json_links = json_obj.get('_links')
    if not json_links:
        obj.links = {}
    else:
        obj_links = {}
        for k, v in json_links.items():
            if 'href' in v:
                href = re.sub("({.+})", "", v['href'])
                if base_url:
                    href = f"{base_url}{href}"
                obj_links[k] = href
            else:
                obj_links[k] = v
        obj.links = obj_links

class Page(list):
    """API response page"""
    def __init__(self, number=None, size=None, total_elements=None, total_pages=None):
        super().__init__([])
        self.number = number
        self.size = size
        self.total_elements = total_elements
        self.total_pages = total_pages

    @staticmethod
    def from_json(json_obj):
        """Instantiate and return a Page(list)"""
        pg = Page()
        pg.number = json_obj['page']['number']
        pg.size = json_obj['page']['size']
        pg.total_pages = json_obj['page']['totalPages']
        pg.total_elements = json_obj['page']['totalElements']
        _assign_links(pg, json_obj)
        # Assuming implementation for adding items to the page based on 'events', 'venues', etc.
        return pg

class Event:
    """Ticketmaster event"""
    def __init__(self, event_id=None, name=None, start_date=None, start_time=None, status=None, classifications=None, links=None):
        self.id = event_id
        self.name = name
        self.start_date = start_date
        self.start_time = start_time
        self.status = status
        self.classifications = classifications
        self.links = links

    @staticmethod
    def from_json(json_event):
        """Creates an `Event` from API's JSON response"""
        e = Event()
        e.id = json_event.get('id')
        e.name = json_event.get('name')
        # Additional attributes setup
        _assign_links(e, json_event)
        return e

    async def fetch_additional_details(self):
        """Asynchronously fetch additional event details (hypothetical example)"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.links['self']) as response:
                details = await response.json()
                # Process and update event instance with additional details

class Venue:
    """A Ticketmaster venue."""
    def __init__(self, name=None, address=None, city=None, state_code=None,
                 postal_code=None, latitude=None, longitude=None,
                 markets=None, url=None, box_office_info=None,
                 dmas=None, general_info=None, venue_id=None,
                 social=None, timezone=None, images=None,
                 parking_detail=None, accessible_seating_detail=None,
                 links=None):
        self.name = name
        self.id = venue_id
        self.address = address
        self.postal_code = postal_code
        self.city = city
        self.state_code = state_code
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.url = url
        self.box_office_info = box_office_info
        self.dmas = dmas
        self.markets = markets
        self.general_info = general_info
        self.social = social
        self.images = images
        self.parking_detail = parking_detail
        self.accessible_seating_detail = accessible_seating_detail
        self.links = links

    @property
    def location(self):
        """Location-based data (full address, lat/lon, timezone)"""
        return {
            'address': self.address,
            'postal_code': self.postal_code,
            'city': self.city,
            'state_code': self.state_code,
            'timezone': self.timezone,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

    @staticmethod
    def from_json(json_venue):
        """Returns a `Venue` object from JSON"""
        v = Venue()
        v.id = json_venue.get('id')
        v.name = json_venue.get('name')
        v.url = json_venue.get('url')
        v.postal_code = json_venue.get('postalCode')
        v.timezone = json_venue.get('timezone')
        v.address = json_venue['address'].get('line1')
        v.city = json_venue['city'].get('name')
        v.state_code = json_venue['state'].get('stateCode')
        v.latitude = json_venue['location'].get('latitude')
        v.longitude = json_venue['location'].get('longitude')
        # Process additional attributes as before
        _assign_links(v, json_venue)
        return v

    async def fetch_additional_details(self, api_client):
        """Asynchronously fetch additional venue details.
        
        Args:
            api_client: Instance of an asynchronous API client.
        """
        # Example URL construction, adjust based on your API's design
        details_url = self.links.get('self', '')  # Assuming 'self' link is detailed info
        if details_url:
            additional_details = await api_client.get(details_url)
            # Process and integrate additional_details into the Venue instance
            print(additional_details)  # Placeholder for actual processing logic

    def __str__(self):
        return f"{self.name} at {self.address} in {self.city} {self.state_code}"

class Attraction:
    """Attraction"""
    def __init__(self, attraction_id=None, attraction_name=None, url=None,
                 classifications=None, images=None, test=None, links=None):
        self.id = attraction_id
        self.name = attraction_name
        self.url = url
        self.classifications = classifications
        self.images = images
        self.test = test
        self.links = links

    @staticmethod
    def from_json(json_obj):
        """Convert JSON object to `Attraction` object"""
        att = Attraction()
        att.id = json_obj.get('id')
        att.name = json_obj.get('name')
        att.url = json_obj.get('url')
        att.test = json_obj.get('test', False)  # Assuming 'test' is a boolean field
        att.images = json_obj.get('images', [])
        classifications = json_obj.get('classifications', [])
        att.classifications = [Classification.from_json(cl) for cl in classifications]
        _assign_links(att, json_obj)
        return att

    async def fetch_additional_details(self, api_client):
        """Asynchronously fetch additional details for the attraction.
        
        Args:
            api_client: Instance of an asynchronous API client capable of making GET requests.
        """
        details_url = self.links.get('self', '')  # Example, adjust based on actual API design
        if details_url:
            async with api_client.session.get(details_url) as response:
                details_json = await response.json()
                # Here you would process the details_json to extract and integrate additional details
                print(details_json)  # Placeholder for actual logic

    def __str__(self):
        return self.name if self.name is not None else 'Unknown'


class Classification:
    """Classification object (segment/genre/sub-genre)"""
    def __init__(self, segment=None, classification_type=None, subtype=None, primary=None, links=None):
        self.segment = segment
        self.type = classification_type
        self.subtype = subtype
        self.primary = primary
        self.links = links

    @staticmethod
    def from_json(json_obj):
        cl = Classification()
        cl.primary = json_obj.get('primary')

        if 'segment' in json_obj:
            cl.segment = Segment.from_json(json_obj['segment'])

        if 'type' in json_obj:
            cl.type = ClassificationType(json_obj['type']['id'], json_obj['type']['name'])

        if 'subType' in json_obj:
            cl.subtype = ClassificationSubType(json_obj['subType']['id'], json_obj['subType']['name'])

        _assign_links(cl, json_obj)
        return cl

    def __str__(self):
        return str(self.type)

    # Hypothetical async method to fetch additional details
    async def fetch_additional_details(self, api_client):
        """Asynchronously fetch additional classification details."""
        # This method is hypothetical and assumes there's a relevant URL in self.links
        details_url = self.links.get('details')  # Assuming 'details' is a key in links
        if details_url:
            async with api_client.session.get(details_url) as response:
                details_json = await response.json()
                # Process details_json as needed

class EventClassification:
    """Classification as it's represented in event search results"""
    def __init__(self, genre=None, subgenre=None, segment=None, classification_type=None, classification_subtype=None, primary=None, links=None):
        self.genre = genre
        self.subgenre = subgenre
        self.segment = segment
        self.type = classification_type
        self.subtype = classification_subtype
        self.primary = primary
        self.links = links

    @staticmethod
    def from_json(json_obj):
        ec = EventClassification()
        ec.primary = json_obj.get('primary')

        if 'segment' in json_obj:
            ec.segment = Segment.from_json(json_obj['segment'])

        if 'genre' in json_obj:
            ec.genre = Genre.from_json(json_obj['genre'])

        if 'subGenre' in json_obj:
            ec.subgenre = SubGenre.from_json(json_obj['subGenre'])

        if 'type' in json_obj:
            ec.type = ClassificationType(json_obj['type']['id'], json_obj['type']['name'])

        if 'subType' in json_obj:
            ec.subtype = ClassificationSubType(json_obj['subType']['id'], json_obj['subType']['name'])

        _assign_links(ec, json_obj)
        return ec

    def __str__(self):
        return f"Segment: {self.segment} / Genre: {self.genre} / Subgenre: {self.subgenre} / Type: {self.type} / Subtype: {self.subtype}"


class ClassificationType:
    def __init__(self, type_id=None, type_name=None, subtypes=None):
        self.id = type_id
        self.name = type_name
        self.subtypes = subtypes

    def __str__(self):
        return self.name if self.name is not None else 'Unknown'

# No changes needed here unless dynamic fetching of subtype details becomes necessary

class ClassificationSubType:
    def __init__(self, type_id=None, type_name=None):
        self.id = type_id
        self.name = type_name

    def __str__(self):
        return self.name if self.name is not None else 'Unknown'

# Similar to ClassificationType, asynchronous behavior might be added for dynamic data fetching

class Segment:
    def __init__(self, segment_id=None, segment_name=None, genres=None, links=None):
        self.id = segment_id
        self.name = segment_name
        self.genres = genres  # Could be a list of Genre instances
        self.links = links

    @staticmethod
    def from_json(json_obj):
        seg = Segment()
        seg.id = json_obj['id']
        seg.name = json_obj.get('name')
        # Processing embedded genres if available
        if '_embedded' in json_obj:
            genres = json_obj['_embedded'].get('genres', [])
            seg.genres = [Genre.from_json(g) for g in genres]
        _assign_links(seg, json_obj)
        return seg

    def __str__(self):
        return self.name if self.name is not None else 'Unknown'

# Could integrate asynchronous methods if genres require fetching additional details

class Genre:
    def __init__(self, genre_id=None, genre_name=None, subgenres=None, links=None):
        self.id = genre_id
        self.name = genre_name
        self.subgenres = subgenres  # Could be a list of SubGenre instances
        self.links = links

    @staticmethod
    def from_json(json_obj):
        g = Genre()
        g.id = json_obj.get('id')
        g.name = json_obj.get('name')
        if '_embedded' in json_obj:
            subgenres = json_obj['_embedded'].get('subgenres', [])
            g.subgenres = [SubGenre.from_json(sg) for sg in subgenres]
        _assign_links(g, json_obj)
        return g

    def __str__(self):
        return self.name if self.name is not None else 'Unknown'

# Asynchronous enhancements could be added for dynamic subgenre data fetching

class SubGenre:
    def __init__(self, subgenre_id=None, subgenre_name=None, links=None):
        self.id = subgenre_id
        self.name = subgenre_name
        self.links = links

    @staticmethod
    def from_json(json_obj):
        sg = SubGenre()
        sg.id = json_obj['id']
        sg.name = json_obj['name']
        _assign_links(sg, json_obj)
        return sg

    def __str__(self):
        return self.name if self.name is not None else 'Unknown'

# Example async usage to fetch and process event details
async def main():
    event = Event.from_json({'id': '123', 'name': 'Sample Event', 'links': {'self': 'http://example.com/event/123'}})
    await event.fetch_additional_details()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
