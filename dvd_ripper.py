# /mnt/3D21ED0D3BAA70C9/Media/Movies

from makemkv import MakeMKV


class MakeMKVHelper:
    def __init__(self, drive_path='/dev/sr0'):
        self.makemkv: MakeMKV = MakeMKV(drive_path)

    def get_disc_information(self) -> (str, list):
        disc_info = self.makemkv.info()
        film_name: str = disc_info["disc"]["name"]
        tracks: list = []
        count: int = 0
        for k in disc_info["titles"]:
            track: dict = {"track_number": count, "name": k["file_output"], "bit_size": k["size"],
                     "human_size": k["size_human"], "duration": k["length"]}
            tracks.append(track)
            count += 1
        tracks: list = sorted(tracks, key=lambda d: d['bit_size'], reverse=True)
        return film_name, tracks

    def make_movie(self, track_number: str, save_location: str):
        self.makemkv.mkv(track_number, save_location)
