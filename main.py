import time
from datetime import datetime
import Communications.WhatsappAPI as WhatsappAPI
import threading
import sys
import signal
from flask import Flask, request, Response
import os
from dotenv import load_dotenv
from waitress import serve
from dvd_ripper import MakeMKVHelper

'''
Status:
    starting
    started
    awaiting_insert
    awaiting_film_name
    decrypting_movie
    analysing_tracks
    awaiting_track_choice
    copy_movie
    copying_movie
'''

load_dotenv()
app: Flask = Flask(__name__)

# Variables
packet_count: int = 0
status: dict = {"status": "starting", "timestamp": datetime.now()}
movie_name: str = None
file_name: str = None
tracks: list = []
track_id: int = None
makeMKV: MakeMKVHelper = MakeMKVHelper()


def set_status(new_status: str) -> None:
    global status
    status["status"]: str = new_status
    status["timestamp"]: datetime = datetime.now()


def rename_movie() -> None:
    time.sleep(0.5)
    global tracks
    for track in tracks:
        if int(track["track_number"]) == int(track_id):
            os.rename(f'{os.environ["movie_save_path"]}/{track["name"]}',
                      f'{os.environ["movie_save_path"]}/{movie_name}.mkv')


def copy_movie() -> None:
    global track_id
    global movie_name
    set_status("copying_movie")
    msg: WhatsappAPI.NewMessage = WhatsappAPI.NewMessage()
    msg.configure_text_request("Started Copying process 💾. This may take a while, make a coffee in the meantime! ☕️")
    msg.send()
    makeMKV.make_movie(int(track_id), f"{os.environ['movie_save_path']}")
    set_status("copy_complete")
    msg: WhatsappAPI.NewMessage = WhatsappAPI.NewMessage()
    msg.configure_text_request("🥳 Copy Complete 🥳")
    msg.send()
    rename_movie()
    dvd_rip()
    # Repeat loop


def analyse_tracks() -> None:
    global track_id
    global tracks
    largest_bit_size: int = max(int(track["bit_size"]) for track in tracks)
    similar_sized_tracks: bool = False
    size_range: int = 100_000_000
    for track in tracks:
        if int(track["bit_size"]) >= (largest_bit_size - size_range) and int(track["bit_size"]) != largest_bit_size:
            similar_sized_tracks = True
    if not similar_sized_tracks:
        # not a similar size
        msg: WhatsappAPI.NewMessage = WhatsappAPI.NewMessage()
        msg.configure_text_request("Tracks analysed successfully 👍!")
        msg.send()
        for track in tracks:
            if int(track["bit_size"]) == largest_bit_size:
                track_id = track["track_number"]
        set_status("copy_movie")
        copy_movie()
    else:
        msg: WhatsappAPI.NewMessage = WhatsappAPI.NewMessage()
        track_rows: list[dict[str,str]] = []
        for track in tracks:
            track_rows.append(WhatsappAPI.MessageHelper.section_row_template(track["track_number"],
                                                                             f'{track["name"]} - {track["human_size"]}',
                                                                             f'Duration: {track["duration"]}'))
        track_sections: dict[str,any] = WhatsappAPI.MessageHelper.section_template("Tracks", track_rows)
        msg.configure_list_request("Track choice 🤷‍♂️",
                                   "Tracks share similar file sizes 📁",
                                   "🔛 Select track 🔛",
                                   [track_sections])
        msg.send()
        set_status("awaiting_track_choice")


def decrypt_disk() -> None:
    global file_name
    global tracks
    msg: WhatsappAPI.NewMessage = WhatsappAPI.NewMessage()
    msg.configure_text_request(f"Decompiling and decrypting '{movie_name}' 🔐 - This may take a while 🕣")
    msg.send()
    global makeMKV
    file_name, tracks = makeMKV.get_disc_information()
    msg: WhatsappAPI.NewMessage = WhatsappAPI.NewMessage()
    msg.configure_text_request(f"'{movie_name}' decompiled and decrypted! 🎉")
    msg.send()
    set_status("analysing_tracks")
    analyse_tracks()


def analysis_incoming_packet(pkt) -> None:
    pkt_messages = pkt["entry"][0]["changes"][0]["value"]["messages"][0]
    global status
    global movie_name
    global track_id
    if status["status"] == "awaiting_insert":
        if pkt_messages["type"] == "interactive":
            if pkt_messages["interactive"]["button_reply"]["id"] == "start":
                set_status("awaiting_film_name")
                msg: WhatsappAPI.NewMessage = WhatsappAPI.NewMessage()
                msg.configure_text_request("Send the movies title 🍿")
                msg.send()
    elif status["status"] == "awaiting_film_name":
        if pkt_messages["type"] == "text":
            movie_name = pkt_messages["text"]["body"]
            set_status("decrypting_movie")
            decrypt_disk()
    elif status["status"] == "awaiting_track_choice":
        if pkt_messages["type"] == "interactive":
            track_id = pkt_messages["interactive"]["list_reply"]["id"]
            set_status("copy_movie")
            copy_movie()


@app.route(os.environ['webhook_api_path'], methods=['GET'])
def verify_webhook():
    if request.method == 'GET':
        verify_token: str = request.args.get('hub.verify_token')
        mode: str = request.args.get('hub.mode')
        challenge: str = request.args.get('hub.challenge')
        if verify_token is not None and mode is not None and challenge is not None:
            challenge = int(challenge)
            if mode == "subscribe":
                if os.environ['verify_token'] == verify_token:
                    return str(challenge)
    return Response(status=400)


@app.route(os.environ['webhook_api_path'], methods=['POST'])
def recieve_message():
    global packet_count
    packet_count += 1
    incoming_data: dict = request.json
    if "'messages':" in str(incoming_data):
        analysis_incoming_packet(incoming_data)
    return Response(status=200)


def run_flask_app() -> None:
    try:
        serve(app, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"> {e}")


def signal_handler(signal, frame):
    sys.exit(0)


def run_webhook() -> None:
    signal.signal(signal.SIGINT, signal_handler)
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()


def reset_variables() -> None:
    global movie_name
    movie_name = None
    global file_name
    file_name = None
    global tracks
    tracks = []
    global track_id
    track_id = None


def dvd_rip() -> None:
    # Start of the ripping "loop"
    reset_variables()
    set_status("started")
    msg: WhatsappAPI.NewMessage = WhatsappAPI.NewMessage()
    msg.configure_button_request("Press 'start' after inserting a disk",
                                 "💿 Ready to rip 💿",
                                 [WhatsappAPI.MessageHelper.button_template("start", "Start")])
    msg.send()
    set_status("awaiting_insert")


def setup_webhook() -> bool:
    msg: WhatsappAPI.NewMessage = WhatsappAPI.NewMessage()
    msg.configure_text_request("Starting, please wait..")
    msg.send()
    run_webhook()
    while packet_count == 0:
        pass
    time.sleep(5)
    set_status("started")
    return True


if __name__ == "__main__":
    time.sleep(5)
    if setup_webhook():
        dvd_rip()
