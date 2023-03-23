## YouTube Video Details for Home Assistant

![release_badge](https://img.shields.io/github/v/release/hokiebrian/youtube_details?style=for-the-badge)
![release_date](https://img.shields.io/github/release-date/hokiebrian/youtube_details?style=for-the-badge)
[![License](https://img.shields.io/github/license/hokiebrian/youtube_details?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

## Installation

This provides a sensor that shows details of a YouTube Video by Title. This can be used to show details for a currently playing YouTube Video on a media player where you only have the Title available (such as AppleTV).

### Install Custom Components

1) Make sure that [Home Assistant Community Store (HACS)](https://github.com/custom-components/hacs) is setup.
2) Go to integrations in HACS
3) Click the 3 dots in the top right corner and choose `Custom repositories`
4) Paste the following into the repository input field `https://github.com/hokiebrian/youtube_details` and choose category of `Integration`
5) Click add and restart HA to let the integration load
6) Go to settings and choose `Devices & Services`
7) Click `Add Integration` and search for `YouTube Video Search`
8) Configure the integration by copying your `YouTube API Key` when prompted

## Usage

Use an automation that is triggered by a Title change on YouTube Media, call the service `youtube_search.search_video` and fill in the mandatory field `video_title`. The service will update `sensor.youtube_search` with the video ID in the state field and all of the video attributes as attributes.  