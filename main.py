# -*- coding: utf-8 -*-
import argparse
import re
import requests
import sys
import websocket
from datetime import datetime

def record_twitcasting(user, proxy='', user_agent='', filename=''):
    try:
        stream_url = get_stream_url(user, proxy=proxy, user_agent=user_agent)
        print(stream_url)

        try:
            # Default filename
            filename = filename if filename else datetime.now().strftime('record_' + user + '_%Y%m%d_%H%M%S.ts')

            output_fd = open(filename, 'wb')
            print(f'Writing stream to {filename}')

            def on_message(ws, data):
                try:
                    output_fd.write(data)
                    sys.stderr.write('.')
                    sys.stderr.flush()
                except IOError as err:
                    print(f'Error when writing to output: {err}, exiting')
                    ws.close()

            def on_error(ws, error):
                print(error)

            def on_close(ws):
                print('Disconnected from WebSocket server')

            ws = prepare_websocket(stream_url,
                header={ 'Origin': f'https://twitcasting.tv/{user}', 'User-Agent': user_agent },
                on_message=on_message,
                on_error=on_error,
                on_close=on_close)

            # Parse proxy string to host and port
            proxy_host, proxy_port = parse_proxy_host_port(proxy)
            ws.run_forever(http_proxy_host=proxy_host, http_proxy_port=proxy_port)

            # Disconnected
            print("Closing file stream...")
            output_fd.close()

        except Exception as err:
            print('Failed to connect to WebSocket server', err)
        finally:
            if output_fd:
                output_fd.close()

    except Exception as err:
        # print('Exception caught:', err)
        raise err


def _get_stream_info(user, proxy='', user_agent=''):
    url = f'https://twitcasting.tv/streamserver.php?target={user}&mode=client'
    r = requests.get(url, proxies={ 'http': proxy, 'https': proxy }, headers={ 'User-Agent': user_agent })
    data = r.json()
    return data


def check_live_status(user, proxy='', user_agent=''):
    data = _get_stream_info(user, proxy, user_agent)
    return data['movie']['live']


def get_stream_url(user, proxy='', user_agent=''):
    data = _get_stream_info(user, proxy, user_agent)

    # Check live stream
    if not data['movie']['live']:
        print(f'Live stream of user {user} is offline')
        return

    if data['fmp4']['source']:
        # High quality
        mode = 'main'
    elif data['fmp4']['mobilesource']:
        # Medium quality
        mode = 'mobilesource'
    else:
        # Low quality
        mode = 'base'

    proto = data['fmp4']['proto']
    host = data['fmp4']['host']
    movie_id = data['movie']['id']

    if (proto == '') or (host == '') or (not movie_id):
        print(f'No stream available for user {user}')
        return

    try: 
        stream_url = data['llfmp4']['streams']['main']
    except: 
         # fallback 
         # 1st number variable: 0 - no compression, 1 - compression
         # 2nd number variable: bufferOffset  
        stream_url = f'{proto}://{host}/ws.app/stream/{movie_id}/fmp4/bd/1/1500?mode={mode}'
    return stream_url


def prepare_websocket(url, **kwargs):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url, **kwargs)
    return ws


def parse_proxy_host_port(proxy_str):
    host = ''
    port = ''

    try:
        proxy_regex = r'(.*)://(.*):([0-9]+)'
        match = re.match(proxy_regex, proxy_str)

        if match:
            host = match.group(2)
            port = match.group(3)
    except Exception:
        pass

    return host, port


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TwitCasting live stream recorder.')

    parser.add_argument('--proxy', help='Request with HTTP proxy. e.g. http://127.0.0.1:1080')
    parser.add_argument('--user-agent', help='Request with custom User Agent.', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0')
    parser.add_argument('-o', '--output', dest='filename', help='File name to save recorded video.')
    parser.add_argument('user_id', help='The user id to record. i.e. the string after "https://twitcasting.tv/" in URL')

    args = parser.parse_args()
    print("Args:", args)
    record_twitcasting(args.user_id, proxy=args.proxy, user_agent=args.user_agent, filename=args.filename)
