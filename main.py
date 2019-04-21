import sys
import socket
import threading
import time
import random
import argparse
import json

import cv2 as cv
import numpy as np

sock: socket.socket = None
UDP_IP: str = "192.168.178.54"
UDP_PORT: int = 42042
MAX_PACKET_SIZE: int = 8000

CURRENT_IMAGE: np.ndarray = None
TARGET_FPS: float = 30.0

lock: threading.Lock = threading.Lock()


def start_udp_server(args):
    """
    Initializes the udp server
    :return:
    """
    print("Server Meta:")
    print("  > UDP target IP:", args.ip)
    print("  > UDP target port:", str(args.port))
    print("  > UDP max packet_size:", str(args.packet_size))

    # send via network using udp
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    d = dict()
    d['ip'] = args.ip
    d['port'] = args.port
    d['packet_size'] = args.packet_size

    # start sending thread
    udp_thread: threading.Thread = threading.Thread(target=send_jpeg_image, args=(d,))
    udp_thread.start()


def send_jpeg_image(config: dict):
    """
    :return:
    """

    ip = config['ip']
    port = config['port']
    packet_size = config['packet_size']

    while True:
        # continue if there is no image
        if CURRENT_IMAGE is None:
            continue

        # encode image to jpg
        with lock:
            success, encoded = cv.imencode('.jpg', CURRENT_IMAGE)

        # if the image could not be encoded continue
        if not success:
            continue

        # get image size in memory
        image_memory_size = sys.getsizeof(encoded)

        # calculate the amount of needed chunks
        num_chunks = int(image_memory_size / packet_size) + 1

        # split element in to chunks
        last_chunk_end = 0

        # generate random image id
        image_id = random.randint(10, 99)

        for chunk_id in range(num_chunks):
            chunk_begin = last_chunk_end
            chunk_end = last_chunk_end + packet_size

            # if the current set chunk end is > the encoded image length
            if chunk_end >= len(encoded):
                chunk_end = len(encoded)

            # reset last chunk end
            last_chunk_end = chunk_end

            # create chunk and convert to bytes
            chunk = encoded[chunk_begin:chunk_end]
            chunk_bytes = chunk.tobytes()

            # create chunk id string
            chunk_id_str = None
            if chunk_id < 10:
                chunk_id_str = "0" + str(chunk_id)
            else:
                chunk_id_str = str(chunk_id)

            # build chunk prefix
            prefix = None
            if chunk_id == 0:
                prefix = str.encode("S") + str.encode(str(image_id)) + chunk_id_str.encode()
            elif chunk_id == num_chunks - 1:
                prefix = str.encode("E") + str.encode(str(image_id)) + chunk_id_str.encode()
            else:
                prefix = str.encode("C") + str.encode(str(image_id)) + chunk_id_str.encode()

            # create chunk bytes object preceeded by the respective meta info
            chunk_bytes = prefix + chunk_bytes

            # send chunk
            sock.sendto(chunk_bytes, (ip, port))

        time.sleep(1 / TARGET_FPS)


def start_video_capture(camera_config: dict, capture_area: dict = None):
    """
    Starts the webcam capture
    :return:
    """
    # start capture thread
    t = threading.Thread(target=capture_stream, args=(camera_config, capture_area))
    t.start()
    return t


def capture_stream(camera_config: dict, capture_area: dict):
    """
    Image capture callback
    :return:
    """
    print(camera_config)
    print(capture_area)
    VIDEO_CAPTURE = cv.VideoCapture(0)
    VIDEO_CAPTURE.set(cv.CAP_PROP_FRAME_WIDTH, camera_config['width'])
    VIDEO_CAPTURE.set(cv.CAP_PROP_FRAME_HEIGHT, camera_config['height'])
    VIDEO_CAPTURE.set(cv.CAP_PROP_FPS, camera_config['fps'])
    while VIDEO_CAPTURE.isOpened():
        ret, frame = VIDEO_CAPTURE.read()
        global CURRENT_IMAGE
        with lock:
            CURRENT_IMAGE = frame


def load_json_file(filename: str):
    d: dict = dict()
    with open(filename, 'r') as jsonfile:
        d = json.load(jsonfile)
    return d


def main():
    """
    Main function
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--area', dest='capture_area', type=str,
                        help='Specify a json file where a capturing area is specified.')
    parser.add_argument('--camera_config', dest='camera', type=str,
                        help='Specify a json file where a camera config is specified.')
    parser.add_argument('--ip', dest='ip',
                        help='Specify the receivers ip.')
    parser.add_argument('--port', dest='port', type=int,
                        help='Specify the receivers port.')
    parser.add_argument('--packet_size', dest='packet_size', type=int,
                        help='Specify the udp packet size.')
    parser.add_argument('--fps', dest='fps', type=int,
                        help='Specify the target sending fps.')
    args = parser.parse_args()

    capture_area = None
    camera_config = None

    if args.capture_area is not None:
        capture_area = load_json_file(args.capture_area)
    if args.camera is not None:
        camera_config = load_json_file(args.camera)

    udp_thread = start_udp_server(args)
    capture_thread = start_video_capture(camera_config, capture_area)


if __name__ == "__main__":
    main()
