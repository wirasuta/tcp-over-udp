# TCP Over UDP

Dalam tugas besar ini, kalian akan meniru tingkah laku TCP (Transmission Control Protocol) di atas socket berbasis UDP (User Datagram Protocol). Adapun cara protokol TCP bekerja adalah sebagai berikut :

![TCP Data Loss Transfer Schema](https://accedian.com/wp-content/uploads/2018/09/tcp3.png)

Dapat terlihat bahwa untuk setiap data yang terkirim, maka receiver akan mengirimkan ACK kepada sender tersebut. Apabila ACK tersebut tidak diterima, maka sender akan mengirimkan data yang sama kembali, hingga seluruh data diterima dengan baik.

Oleh karena itu, anda memerlukan beberapa tipe paket untuk dapat mensimulasikan hal tersebut. Berikut merupakan diagram spesifikasi paket yang akan anda implementasikan.

```
| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| TYPE (4 bits) |  ID (4 bits)  |
|---|---|---|---|---|---|---|---|
|   SEQUENCE NUMBER (16 bits)   |
|---|---|---|---|---|---|---|---|
|       LENGTH (16 bits)        |
|---|---|---|---|---|---|---|---|
|      CHECKSUM (16 bits)       |
|---|---|---|---|---|---|---|---|
|             DATA              |
|           MAX 32KB            |
|---|---|---|---|---|---|---|---|
```

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and deployment purposes.

### TODOs

Mind you this project is incomplete. This are the TODOs

- Increase acknowledgement efficiency or decrease critical section size
- Progress bar
- Increase memory efficiency (read file partially, double buffering, use generator)

### Prerequisites

Python 3.6+ is needed to run this project. To check your python version use

```
python3 -V
```

### Installing

To run the project simply clone the repository and start the `receiver.py` . It will ask port to bind and use default loopback as host

```
$ ./receiver.py
Enter port to bind:
```

To start sending data, run the `sender.py` which will ask for destination ip and port, timeout before retrying to send packet, and files to send

```
$ ./sender.py
Enter destination (IP):
Enter destination (Port):
Timeout (s):
Files to send (Separated by comma):
```

You might need to add run privilege to both script to run them as demonstrated

```
$ chmod +x sender.py
$ chmod +x receiver.py
```

## Built With

- [Python 3](https://docs.python.org/3/) - The language and all its built in library

## Authors

- **Wirasuta** - _Initial work_
- **Bariansyah** - _Packet class definition_
- **Gardahadi**

## Acknowledgments

- IF3130 Computer Network Assistants
