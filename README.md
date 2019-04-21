# UDP Webcam Server
Implemented using python version 3.7.2

This is a fairly simple image sending server. Images are captured using an OpenCV `cv2.VideoCapture()` object. The default selected device has the id 0. The UDP server simply jpeg-encodes the image and splits it in `image_memory_size / max_packet_size` chunks. The size of each chunk is determined by the set maximum packet size + 5. Each transmitted chunk contains 5bytes of meta info preceeding the actual image byte array.

| Chunk Type | Image Id | Chunk Id | Imagedata |
|------------|----------|----------|-----------|
| S          | 22       | 00       | .....     |
| C          | 22       | 01       | .....     |
| E          | 22       | 02       | .....     |

Where S marks the beginning of an image, C a central part, E the end of an image. For each image there is a random two digit Id created. Each Chunk is numerated. The last 4 bytes of information is used by the receiving side to reconstruct an image.

## Requirements
future==0.17.1
numpy==1.16.2
opencv-python==4.1.0.25

Either install requirements manually or by calling `requirements.txt`
```
pip install -r requirements.txt
```
## Executing
There is a set of parameters that are necessary:

### Capuring area: '--area'
Specify a json file where a capturing area is specified.

Must meet the following structure:
```
```

### Camera config file: '--camera_config',
Specify a json file where a camera config is specified.

Must meet the following structure:
```
    {
      "width": 640,
      "height": 360,
      "fps": 60
    }
```

### Receiver IP: '--ip'
Specify the receivers ip where the image chunks are sent to.

### Receiver Port: '--port'
Specify the receivers port.

### Capuring area:k '--packet_size'
Specify the maximum udp packet size.

### Capuring area:k '--fps'
Specify the target sending fps.
