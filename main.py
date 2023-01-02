from makemkv import MakeMKV


def get_disc_information(makemkv):
    disc_info = makemkv.info()
    film_name = disc_info["disc"]["name"]
    tracks = []
    count = 0
    for k in disc_info["titles"]:
        track = {}
        track["track_number"] = count
        track["name"] = k["file_output"]
        track["bit_size"] = k["size"]
        track["human_size"] = k["size_human"]
        track["duration"] = k["length"]
        tracks.append(track)
        count += 1
    return film_name, tracks


def display_tracks(tracks):
    for i in range(len(tracks)):
        print(f"{i} - {tracks[i]}")


def make_movie(makemkv, track_number):
    return None
    makemkv.mkv(track_number, "/home/james/Documents/test_files")

def sort_chapter_list(tracks):
    return sorted(tracks, key=lambda d: d['bit_size'], reverse=True)


if __name__ == "__main__":
    print(f'instantiating MakeMKV')
    makemkv = MakeMKV('/dev/sr0')
    print(f"instantiated MakeMKV")

    print(f"getting movie information")
    name, tracks = get_disc_information(makemkv)
    tracks = sort_chapter_list(tracks)
    print(f"retrieved movie information")
    display_tracks(tracks)
    track = int(input("pick a track"))

    print(f'making movie')
    make_movie(makemkv, tracks[track]["track_number"])
    print(f'finished making movie')
