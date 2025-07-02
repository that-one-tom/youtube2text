from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import re
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def extract_video_id(url_or_id):
    """Extract video ID from YouTube URL or return the ID if it's already an ID"""
    if not url_or_id:
        return None
    
    # If it's already a video ID (11 characters, alphanumeric and some special chars)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # Extract from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return None

def parse_proxy_config(proxy_string):
    """Parse proxy configuration from query parameter
    
    Supports formats:
    - http://proxy.example.com:8080
    - http://username:password@proxy.example.com:8080
    - https://proxy.example.com:8080
    """
    if not proxy_string:
        return None
    
    try:
        # Basic validation
        if not proxy_string.startswith(('http://', 'https://')):
            proxy_string = 'http://' + proxy_string
        
        # Return proxy configuration for requests and yt-dlp
        return {
            'http': proxy_string,
            'https': proxy_string
        }
    except Exception as e:
        app.logger.warning(f"Invalid proxy configuration: {proxy_string}, error: {str(e)}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'youtube2text-api'})

@app.route('/transcript', methods=['GET'])
def get_transcript():
    """Get transcript for a YouTube video"""
    try:
        video_id = request.args.get('video_id')
        if not video_id:
            return jsonify({'error': 'video_id parameter is required'}), 400
        
        # Extract video ID if a full URL is provided
        extracted_id = extract_video_id(video_id)
        if not extracted_id:
            return jsonify({'error': 'Invalid YouTube video ID or URL'}), 400
        
        # Optional parameters
        languages = request.args.get('languages', 'en').split(',')
        proxy = request.args.get('proxy')
        
        # Parse proxy configuration
        proxy_config = parse_proxy_config(proxy)
        if proxy:
            app.logger.info(f"Using proxy for transcript request: {proxy}")
        
        def get_transcript_with_proxy(extracted_id, languages, proxy_config):
            """Helper function to get transcript with optional proxy support"""
            if proxy_config:
                import os
                original_http_proxy = os.environ.get('HTTP_PROXY')
                original_https_proxy = os.environ.get('HTTPS_PROXY')
                
                os.environ['HTTP_PROXY'] = proxy_config['http']
                os.environ['HTTPS_PROXY'] = proxy_config['https']
                
                try:
                    return YouTubeTranscriptApi.get_transcript(extracted_id, languages=languages)
                finally:
                    # Restore original proxy settings
                    if original_http_proxy:
                        os.environ['HTTP_PROXY'] = original_http_proxy
                    else:
                        os.environ.pop('HTTP_PROXY', None)
                    
                    if original_https_proxy:
                        os.environ['HTTPS_PROXY'] = original_https_proxy
                    else:
                        os.environ.pop('HTTPS_PROXY', None)
            else:
                return YouTubeTranscriptApi.get_transcript(extracted_id, languages=languages)
        
        try:
            # Try to get transcript in preferred languages
            transcript = get_transcript_with_proxy(extracted_id, languages, proxy_config)
        except Exception as e:
            # If preferred languages fail, try to get any available transcript
            try:
                if proxy_config:
                    import os
                    original_http_proxy = os.environ.get('HTTP_PROXY')
                    original_https_proxy = os.environ.get('HTTPS_PROXY')
                    
                    os.environ['HTTP_PROXY'] = proxy_config['http']
                    os.environ['HTTPS_PROXY'] = proxy_config['https']
                    
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(extracted_id)
                        transcript = transcript_list.find_transcript(['en']).fetch()
                    finally:
                        # Restore original proxy settings
                        if original_http_proxy:
                            os.environ['HTTP_PROXY'] = original_http_proxy
                        else:
                            os.environ.pop('HTTP_PROXY', None)
                        
                        if original_https_proxy:
                            os.environ['HTTPS_PROXY'] = original_https_proxy
                        else:
                            os.environ.pop('HTTPS_PROXY', None)
                else:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(extracted_id)
                    transcript = transcript_list.find_transcript(['en']).fetch()
            except:
                # If English fails, get the first available transcript
                try:
                    if proxy_config:
                        import os
                        original_http_proxy = os.environ.get('HTTP_PROXY')
                        original_https_proxy = os.environ.get('HTTPS_PROXY')
                        
                        os.environ['HTTP_PROXY'] = proxy_config['http']
                        os.environ['HTTPS_PROXY'] = proxy_config['https']
                        
                        try:
                            available_transcripts = YouTubeTranscriptApi.list_transcripts(extracted_id)
                            first_transcript = next(iter(available_transcripts))
                            transcript = first_transcript.fetch()
                        finally:
                            # Restore original proxy settings
                            if original_http_proxy:
                                os.environ['HTTP_PROXY'] = original_http_proxy
                            else:
                                os.environ.pop('HTTP_PROXY', None)
                            
                            if original_https_proxy:
                                os.environ['HTTPS_PROXY'] = original_https_proxy
                            else:
                                os.environ.pop('HTTPS_PROXY', None)
                    else:
                        available_transcripts = YouTubeTranscriptApi.list_transcripts(extracted_id)
                        first_transcript = next(iter(available_transcripts))
                        transcript = first_transcript.fetch()
                except Exception as inner_e:
                    return jsonify({'error': f'No transcript available for video: {str(inner_e)}'}), 404
        
        # Format the response
        formatted_transcript = []
        full_text = ""
        
        for item in transcript:
            formatted_item = {
                'text': item['text'],
                'start': item['start'],
                'duration': item['duration']
            }
            formatted_transcript.append(formatted_item)
            full_text += item['text'] + " "
        
        response = {
            'video_id': extracted_id,
            'transcript': formatted_transcript,
            'full_text': full_text.strip(),
            'total_segments': len(formatted_transcript)
        }
        
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Error getting transcript: {str(e)}")
        return jsonify({'error': f'Failed to get transcript: {str(e)}'}), 500

@app.route('/comments', methods=['GET'])
def get_comments():
    """Get comments for a YouTube video"""
    try:
        video_id = request.args.get('video_id')
        if not video_id:
            return jsonify({'error': 'video_id parameter is required'}), 400
        
        # Extract video ID if a full URL is provided
        extracted_id = extract_video_id(video_id)
        if not extracted_id:
            return jsonify({'error': 'Invalid YouTube video ID or URL'}), 400
        
        # Optional parameters
        limit = request.args.get('limit', type=int)
        sort_by = request.args.get('sort_by', 'top')  # 'top' or 'new'
        proxy = request.args.get('proxy')
        
        # Parse proxy configuration
        proxy_config = parse_proxy_config(proxy)
        if proxy:
            app.logger.info(f"Using proxy for comments request: {proxy}")
        
        # Build the video URL
        video_url = f"https://www.youtube.com/watch?v={extracted_id}"
        
        try:
            # Configure yt-dlp to extract comments
            ydl_opts = {
                'writeinfojson': False,
                'writecomments': True,
                'getcomments': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            # Add proxy configuration if provided
            if proxy_config:
                ydl_opts['proxy'] = proxy_config['http']
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                app.logger.info(f"Extracting comments for video: {extracted_id}")
                info = ydl.extract_info(video_url, download=False)
                
                raw_comments = info.get('comments', [])
                comments = []
                
                # Sort comments based on sort_by parameter
                if sort_by.lower() == 'new':
                    # Sort by timestamp (newest first)
                    raw_comments.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
                else:  # 'top' or default
                    # Sort by like_count (most liked first)
                    raw_comments.sort(key=lambda x: x.get('like_count', 0), reverse=True)
                
                # Process comments
                for comment in raw_comments:
                    comment_data = {
                        'author': comment.get('author', ''),
                        'text': comment.get('text', ''),
                        'votes': comment.get('like_count', 0),
                        'time': comment.get('timestamp', ''),
                        'reply_count': 0,  # yt-dlp doesn't provide reply count in the same way
                        'cid': comment.get('id', ''),
                        'time_parsed': comment.get('timestamp', None)
                    }
                    comments.append(comment_data)
                    
                    # Apply limit if specified
                    if limit and len(comments) >= limit:
                        break
                
                response = {
                    'video_id': extracted_id,
                    'comments': comments,
                    'total_comments': len(comments),
                    'sort_by': sort_by
                }
                
                if limit:
                    response['limited_to'] = limit
                
                return jsonify(response)
            
        except Exception as e:
            app.logger.error(f"Failed to fetch comments for video {extracted_id}: {str(e)}")
            return jsonify({'error': f'Failed to fetch comments: {str(e)}'}), 404
        
    except Exception as e:
        app.logger.error(f"Error getting comments: {str(e)}")
        return jsonify({'error': f'Failed to get comments: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint"""
    docs = {
        'service': 'YouTube2Text API',
        'version': '1.0.0',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/transcript': {
                'method': 'GET',
                'description': 'Get transcript for a YouTube video',
                'parameters': {
                    'video_id': 'YouTube video ID or URL (required)',
                    'languages': 'Comma-separated language codes (optional, default: en)',
                    'proxy': 'Proxy server URL (optional, e.g., http://proxy.example.com:8080)'
                },
                'example': '/transcript?video_id=dQw4w9WgXcQ&languages=en,es&proxy=http://proxy.example.com:8080'
            },
            '/comments': {
                'method': 'GET',
                'description': 'Get comments for a YouTube video',
                'parameters': {
                    'video_id': 'YouTube video ID or URL (required)',
                    'limit': 'Maximum number of comments to return (optional)',
                    'sort_by': 'Sort order: "top" or "new" (optional, default: top)',
                    'proxy': 'Proxy server URL (optional, e.g., http://proxy.example.com:8080)'
                },
                'example': '/comments?video_id=dQw4w9WgXcQ&limit=50&sort_by=top&proxy=http://proxy.example.com:8080'
            }
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
