# YouTube2Text API

This project provides a Dockerized REST API that fetches comments and transcripts from YouTube videos.

## Features
- **GET /comments**: Fetches comments from a YouTube video.
- **GET /transcript**: Retrieves the transcript of a YouTube video.

## Requirements
- Docker
- Docker Compose

## Setup

1. **Clone the repository.**
   ```bash
   git clone <repository-url>
   cd youtube2text
   ```

2. **Build and run the Docker container.**
   ```bash
   docker-compose up --build
   ```

3. **Access the API.**
   The API will be available at `http://localhost:8000`.

## Usage

- **Fetch Comments**
  ```
  GET /comments?video_id=<youtube_video_id>&limit=10&sort_by=top
  ```
- **Fetch Transcript**
  ```
  GET /transcript?video_id=<youtube_video_id>&languages=en,es
  ```

## Endpoints

- `/transcript`: 
  - **Parameters**: 
    - `video_id` (string, required) - YouTube video ID or URL.
    - `languages` (string, optional) - Comma-separated language codes.
- `/comments`:
  - **Parameters**:
    - `video_id` (string, required) - YouTube video ID or URL.
    - `limit` (integer, optional) - Maximum number of comments to return.
    - `sort_by` (string, optional) - Sort order: "top" or "new" (default: top).

## Credits

This project is made possible by the following excellent open-source libraries:

### [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
A Python library that provides a simple interface for retrieving YouTube video transcripts. This library enables the `/transcript` endpoint by handling the complex process of extracting and formatting YouTube's subtitle data.

### [yt-dlp](https://github.com/yt-dlp/yt-dlp)
A feature-rich command-line audio/video downloader and Python library. This project leverages yt-dlp's robust comment extraction capabilities to power the `/comments` endpoint. yt-dlp is a fork of youtube-dl with additional features and improvements, providing reliable access to YouTube metadata including comments.

I am super grateful to the maintainers and contributors of these projects for their hard work in creating and maintaining these essential tools that make this tool possible.

## License

This project is licensed under the MIT License.
