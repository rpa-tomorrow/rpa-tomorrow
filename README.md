# D7017E Substorm - Natural language processing

Project designed and written in Python in conjunction with the D7017E Project in Information and Communication Technology course at Luleå University of Technology.

## Project description

The purpose of the project is to implement a system where the user can write instrutions in clear text using machine learning and natural language processing, in order to instruct the computer what to do.

## Requirements

- Python 3.8.5
- Anaconda

## Setup

Create conda environment to handle dependencies.

    conda env create -f substorm-nlp.yml
    conda activate substorm-nlp

### Python

Add user information to `lib/settings.py`.

Example on how to use the automation module is in `demo.py`

#### Local SMTP server

It can be nice to test the Send automation module using a local SMTP server. This can easily be done by running

```
python -m smtpd -n -c DebuggingServer localhost:1025
```

in your terminal. The SMTP server is now running on `localhost:1025` and the predefined user `John Doe` in `lib/settings.py` can be used to send emails to this local server.

### Linux

Below are the absolute minimum packages you will need for Linux. Names might vary depending on your distribution, you might need to install it manually if you can't find it using your distribution's package manager.

```
Python 3.8.5-1
```

## Build instructions

## Authors

- Viktor From - vikfro-6@student.ltu.se - [viktorfrom](https://github.com/viktorfrom)
- Mark Hakansson - marhak-6@student.ltu.se - [markhakansson](https://github.com/markhakansson)
- Gustav Hansson - gushan-6@student.ltu.se - [97gushan](https://github.com/97gushan)
- Niklas Lundberg - inaule-6@student.ltu.se - [Blinningjr](https://github.com/Blinningjr)
- Alexander Mennborg - aleman-6@student.ltu.se - [Aleman778](https://github.com/Aleman778)
- Hugo Wangler - hugwan-6@student.ltu.se - [banunkers](https://github.com/banunkers)
- Aron Widforss - arowid-6@student.ltu.se - [widforss](https://github.com/widforss)

## License

Licensed under the MIT license. See [LICENSE](LICENSE) for details.
