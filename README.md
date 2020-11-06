# D7017E Substorm - Natural language processing

Project designed and written in Python in conjunction with the D7017E Project in Information and Communication Technology course at Luleå University of Technology.

## Project description

The purpose of the project is to implement a system where the user can write instructions in clear text using machine learning and natural language processing, in order to instruct the computer what to do.

## Requirements

- Python 3.8.5
- Anaconda

## Setup

To create and activate the projects conda environment the setup script can be used with the following command

```
source substorm.sh
```

This will also install all of the required models from the [model releases repository](https://github.com/rpa-tomorrow/model-releases).
Please note that no newly released models will be installed if this script has already been used before. For this to work the conda environment needs to be removed entirely before running the setup script again.

### Manually installing a model

With the conda environment activated a model can be installed by using `pip`

```bash
pip install https://github.com/rpa-tomorrow/model-releases/releases/download/<TAG>.tar.gz
```

where `<TAG>` is the [tag](https://github.com/rpa-tomorrow/model-releases/tags) of the model to install.

### Local SMTP server

It can be nice to test the Send automation module (sends emails) using a local SMTP debugging server. This can be done by running

```
python -m smtpd -n -c DebuggingServer localhost:1025
```

in your terminal. A local SMTP debugging server is now running on `localhost:1025` and the predefined user `John Doe` in [config/user.yaml](config/user.yaml) can be used to send emails to this local server. If an email is sent using the module you should now be able to see it in the terminal.

### Google QAuth 2.0 client secret

Since the [schedule module](lib/automate/modules/schedule.py), responsible for scheduling meetings, uses the Google Calendar API some setup is required
for this module to work.
Follow this [Google guide](https://support.google.com/cloud/answer/6158849?hl=en) and create a Google Calendar API.

The scope of the credentials needs to set to `https://www.googleapis.com/auth/calendar.events.owned`

After that download the credentials and put it in `substorm-nlp/` directory, also name it `client_secret.json`.

Now the schedule module should work and any created meetings should show up in the calendar of the account you created the credentials for.

## Usage

### User input

Since the program is intended to be able to parse and understand clear text as input, to perform various tasks, there is no specific
syntax for the input. However, the program is only able to perform three specific use cases at the moment, these are:

- Sending emails
- Creating reminders
- Scheduling meetings

Because of this the input has to contain a verb connected to one of these use cases in order for the program to understand and invoke a module for execution. Below are the verbs connected to each module, which can be used in the input.

- Send email [send, mail, e-mail, email]
- Reminder [remind, reminder, notify]
- Schedule meeting [book, schedule, meeting]

As long as a module can be invoked after parsing the input you will be prompted about any missing information in the input such as when to schedule the reminder, what should be sent in the email etc.

#### Example input

```bash
remind me to eat in 30 seconds
```

```
send an email to Niklas
```

```
schedule a meeting with John at 13:00
```

### CLI

The CLI can be started as follows

- `cd` into the project folder
- Run `python lib/cli/cli.py`
- You can check available CLI options with the `--help` flag

The CLI should now be running in your terminal. Type `help` for more instructions. See [User input](#user-input) if the program is struggling to understand the input.

## Testing

The tests can be run with the following command

```bash
pytest
```

while inside the project directory. You will need the `pytest-cov` package to run it, this will already be installed if the conda environment is activated when issuing the above command.

A coverage report will automatically be generated and saved in `htmlcov/` and it can be viewed at `htmlcov/index.html`

## Authors

- Viktor From - vikfro-6@student.ltu.se - [viktorfrom](https://github.com/viktorfrom)
- Mark Hakansson - marhak-6@student.ltu.se - [markhakansson](https://github.com/markhakansson)
- Gustav Hansson - gushan-6@student.ltu.se - [97gushan](https://github.com/97gushan)
- Niklas Lundberg - inaule-6@student.ltu.se - [Blinningjr](https://github.com/Blinningjr)
- Alexander Mennborg - aleman-6@student.ltu.se - [Aleman778](https://github.com/Aleman778)
- Hugo Wangler - hugwan-6@student.ltu.se - [hugowangler](https://github.com/hugowangler)
- Aron Widforss - arowid-6@student.ltu.se - [widforss](https://github.com/widforss)

## License

Licensed under the MIT license. See [LICENSE](LICENSE) for details.
