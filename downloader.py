import argparse
import logging
import os
import time
from googlesearch import search
import youtube_dl


def title_case(s):
    tokens = s.split()
    name = tokens[0][0].upper() + tokens[0][1:]

    for word in tokens[1:]:
        if word not in ['in', 'the', 'for', 'of', 'a', 'at', 'an', 'is', 'and']:
            name += ' ' + word[0].upper() + word[1:]
        else:
            name += ' ' + word

    return name


def g_search(name):
    return list(search(query=name, tld='co.in', lang='en', num=10, stop=10, pause=2))


def download(url, base_path, idx):
    path = str(os.path.join(base_path, f'{idx}. %(title)s.%(ext)s'))
    print(f"Downloading to {path}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'postprocessor_args': [
            '-ar', '16000'
        ],
        'outtmpl': path,
        'prefer_ffmpeg': True,
        'keepvideo': True,
        'noplaylist': True,
        'forcetitle': True,
        'verbose': False
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.download([url])


def download_song(song, base_path, idx):
    search_query = song + ' youtube'
    links = g_search(search_query)
    print(f"Got links={links}")
    for link in links:
        if "https://www.youtube.com/watch" in link:
            try:
                print(f"Trying {link}")
                if download(link, base_path, idx) != 0:
                    continue
                return True
            except:
                continue
    return None


def main(file_path, base_path):
    os.makedirs(base_path, exist_ok=True)
    error_file_name = os.path.join(base_path, 'failed_songs.txt')
    with open(error_file_name, 'w') as f2:
        with open(file_path) as f:
            for idx, song in enumerate(f.readlines()):
                print("Downloading " + title_case(song))
                try:
                    out = download_song(song, base_path, idx)
                    if out:
                        print("Downloaded " + title_case(song) + "\n")
                    else:
                        print("Failed " + title_case(song) + "\n")

                        print("Retrying in 5 sec")
                        time.sleep(5)
                        out = download_song(song, base_path, idx)
                        if out:
                            print("Downloaded " + title_case(song) + "\n")
                        else:
                            print("Failed " + title_case(song) + "\n")
                            f2.write(song + "\n")
                except Exception as e:
                    logging.exception(e, exc_info=True)
                    print("error in " + title_case(song))
                    f2.write(song)

    test = os.listdir(base_path)
    for item in test:
        if not item.endswith(".mp3"):
            os.remove(os.path.join(base_path, item))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file_path', required=True, type=str, help='Songs list file path (.txt)'
    )
    parser.add_argument(
        '--output_path', required=True, type=str, help='Output directory path'
    )

    # do normal parsing
    args = parser.parse_args()
    main(args.file_path, args.output_path)
