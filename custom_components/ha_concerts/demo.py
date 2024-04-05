import asyncio
import sys
from pathlib import Path
import json

# Calculate the directory containing tmticket and add it to sys.path
#current_dir = Path(__file__).parent
#tmticket_dir = current_dir / 'tmticket'
#sys.path.insert(0, str(tmticket_dir))

from tmticket import AsyncApiClient, EventQuery, VenueQuery, ClassificationQuery, AttractionQuery

async def fetch_events():
    api_client = AsyncApiClient(api_key='D7NjmIfy5i316wqwqjZpGtEiV4lA1pRs')

    event_query = EventQuery(api_client)

    events_data = await event_query.find(keyword="Hozier", locale='en', size=4)

    events = events_data['_embedded']['events']

    for event in events:
        print(event['name'])

    venue_query = VenueQuery(api_client)

#    venues_data = await venue_query.find(keyword='Tabernacle', page=1, size=4)
#    venues = venues_data['_embedded']['venues']

#    for venue in venues:
#        print(venue['name'])

if __name__ == "__main__":
    asyncio.run(fetch_events())
