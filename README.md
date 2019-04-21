# UDP Webcam Server
Implemented using python version
Python 3.7.2

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
