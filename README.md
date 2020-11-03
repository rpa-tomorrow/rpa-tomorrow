# D7017E Substorm - Natural language processing

Project designed and written in Python in conjunction with the D7017E Project in Information and Communication Technology course at Luleå University of Technology.

## Project description

The purpose of the project is to implement a system where the user can write instructions in clear text using machine learning and natural language processing, in order to instruct the computer what to do.

## Requirements

- Python 3.8.5
- Anaconda

## Setup

Create and activate conda environment.
```
source substorm.sh
```

### Python

Add user information to `lib/settings.py`.

Example on how to use the automation module is in `demo.py`

### Testing

The tests can be run with the following command

```bash
pytest
```

while inside the project directory. You will need the `pytest-cov` package to run it.

A coverage report will automatically be generated and and saved in `htmlcov` and it can be viewed at `htmlcov/index.html`

#### Local SMTP server

It can be nice to test the Send automation module (sends emails) using a local SMTP debugging server. This can be done by running

```
python -m smtpd -n -c DebuggingServer localhost:1025
```

in your terminal. A local SMTP debugging server is now running on `localhost:1025` and the predefined user `John Doe` in `lib/settings.py` can be used to send emails to this local server. If an email is sent using the module you should now be able to see it in the terminal.

### Linux

Below are the absolute minimum packages you will need for Linux. Names might vary depending on your distribution, you might need to install it manually if you can't find it using your distribution's package manager.

```
Python 3.8.5-1
```

## Build instructions

## Usage

### CLI

The CLI can be started as follows

- `cd` into the project folder
- Run `python lib/cli/cli.py`
- You can check available CLI options with `--help`

The CLI should now be running in your terminal. Type `help` for more instructions. Currently the CLI is only capable of sending predefined emails if a word similar to `skicka` is entered by the user. Note that you need to have a [local SMTP debugging server](https://github.com/rpa-tomorrow/substorm-nlp/tree/cli-call-automation#local-smtp-server) running for this to work.

## Setup Google QAuth 2.0 client secret

Follow this [Google guide](https://support.google.com/cloud/answer/6158849?hl=en) and create a Google Calendar API.

The scope of the credentials needs to set to `https://www.googleapis.com/auth/calendar.events.owned`

After that download the credentials and put it in `substorm-nlp/` directory, also name it `client_secret.json`.

Now the schedule module should work.

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
