from pytube import YouTube, Playlist


def get_channel_videos(link):
    links = Playlist(link).parse_links()

    if not links:
        return None
    full_links = ["https://www.youtube.com"+link for link in links]
    return full_links


def get_info(link):
    yt = YouTube(link)
    return yt.title, yt.embed_url