# RPi Proxy
This is a simple proxy that communicate with the main server. 

## Requirements

Install the following:
```
sudo  apt-get install git
```
For the Proxy it self:
```
sudo apt install python3
```
```
sudo apt install python3-pip
```
```
pip3 install pyserial
```

## How to connect to [FREE_Web](https://github.com/e-lab-FREE/FREE_Web)
To be able to comunicate with your main server, you need to change the configuration of the proxy you need to edit the following file:

* `server_info.ini` - change the SERVER, PORT with the corresponding to your server and the APPARATUS ID, EXPERIMENT_ID, SECRET corresponding to the information on the database of your main server ([FREE_Web](https://github.com/e-lab-FREE/FREE_Web))

```ini
[DEFAULT]
SERVER = elab1.ist.utl.pt
PORT = 5000
APPARATUS_ID = 2
EXPERIMENT_ID = 2
SECRET = local_help
DEBUG = on
```


after changing the SERVER and PORT to the correct ones that you are using for FREE just run the proxy by:

python3 main.py
