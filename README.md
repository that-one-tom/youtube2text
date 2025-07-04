# YouTube2Text API

This project provides a Dockerized REST API that fetches comments and transcripts from YouTube videos.

## Features
- **GET /comments**: Fetches comments from a YouTube video.
- **GET /transcript**: Retrieves the transcript of a YouTube video.

## Requirements
- Docker
- Docker Compose

## Quick Start (Using Pre-built Image)

The easiest way to get started is using the pre-built Docker image from GitHub Container Registry:

### Using Docker

```bash
# Pull and run the latest image
docker run -p 5000:5000 ghcr.io/that-one-tom/youtube2text:latest
```

The API will be available at `http://localhost:5000`.

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
services:
  youtube2text:
    image: ghcr.io/that-one-tom/youtube2text:latest
    ports:
      - "5000:5000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Then run:

```bash
docker-compose up -d
```

## Proxy Support

Both endpoints support proxy servers to help bypass potential IP blocks from YouTube. Simply add the `proxy` parameter to your requests:

### Proxy Formats Supported:
- `http://proxy.example.com:8080`
- `https://proxy.example.com:8080`
- `http://username:password@proxy.example.com:8080`

### Example Usage:
```bash
# Using proxy with comments endpoint
curl "http://localhost:5000/comments?video_id=dQw4w9WgXcQ&proxy=http://proxy.example.com:8080"

# Using proxy with transcript endpoint
curl "http://localhost:5000/transcript?video_id=dQw4w9WgXcQ&proxy=http://proxy.example.com:8080"
```

**Note:** Proxy support is particularly useful when:
- Making requests from IP addresses that YouTube has rate-limited
- Running the service from regions with YouTube access restrictions
- Needing to distribute load across multiple IP addresses

## Usage

- **Fetch Comments**
  ```
  GET /comments?video_id=<youtube_video_id>&limit=10&sort_by=top&proxy=http://proxy.example.com:8080
  ```
- **Fetch Transcript**
  ```
  GET /transcript?video_id=<youtube_video_id>&languages=en,es&proxy=http://proxy.example.com:8080
  ```

## Endpoints

- `/transcript`: 
  - **Parameters**: 
    - `video_id` (string, required) - YouTube video ID or URL.
    - `languages` (string, optional) - Comma-separated language codes.
    - `proxy` (string, optional) - Proxy server URL (supports http://proxy:port or http://user:pass@proxy:port).
- `/comments`:
  - **Parameters**:
    - `video_id` (string, required) - YouTube video ID or URL.
    - `limit` (integer, optional) - Maximum number of comments to return.
    - `sort_by` (string, optional) - Sort order: "top" or "new" (default: top).
    - `proxy` (string, optional) - Proxy server URL (supports http://proxy:port or http://user:pass@proxy:port).

## Credits

This project is made possible by the following excellent open-source libraries:

### [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
A Python library that provides a simple interface for retrieving YouTube video transcripts. This library enables the `/transcript` endpoint by handling the complex process of extracting and formatting YouTube's subtitle data.

### [yt-dlp](https://github.com/yt-dlp/yt-dlp)
A feature-rich command-line audio/video downloader and Python library. This project leverages yt-dlp's robust comment extraction capabilities to power the `/comments` endpoint. yt-dlp is a fork of youtube-dl with additional features and improvements, providing reliable access to YouTube metadata including comments.

I am super grateful to the maintainers and contributors of these projects for their hard work in creating and maintaining these essential tools that make this tool possible.

## License

This project is licensed under the MIT License.
