# TwitCasting Recorder [WIP]

Just another Python implementation of [TwitCasting](https://twitcasting.tv/) live stream recorder.

## Usage

Install dependencies with `pip install -r requirements.txt`.

```
usage: main.py [-h] [--proxy PROXY] [--user-agent USER_AGENT] [-o FILENAME] user_id

TwitCasting live stream recorder.

positional arguments:
  user_id               The user id to record.
                        i.e. the string after "https://twitcasting.tv/" in URL

optional arguments:
  -h, --help            show this help message and exit
  --proxy PROXY         Request with HTTP proxy. e.g. http://127.0.0.1:1080
  --user-agent USER_AGENT
                        Request with custom User Agent.
  -o FILENAME, --output FILENAME
                        File name to save recorded video.
```

Recorded videos are saved as MPEG-2 TS format, which is designed for live streaming.

You can simply remux them to MP4 format using ffmpeg:

```
ffmpeg -i xxx.ts -codec copy xxx.mp4
```

## Thanks

- [himananiito/livedl](https://github.com/himananiito/livedl)
- [nekoteaparty/Alice-LiveMan](https://github.com/nekoteaparty/Alice-LiveMan)

## License

MIT License (c) 2019 printempw
