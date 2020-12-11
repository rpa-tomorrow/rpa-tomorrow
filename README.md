# RPA Tomorrow - process tasks from natural text

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub release](https://img.shields.io/github/release/rpa-tomorrow/rpa-tomorrow.svg)](https://github.com/rpa-tomorrow/rpa-tomorrow/releases/)
<a href="https://github.com/rpa-tomorrow/rpa-tomorrow/actions"><img alt="Actions Status" src="https://github.com/rpa-tomorrow/rpa-tomorrow/workflows/CI/badge.svg"></a>
<a href="https://github.com/rpa-tomorrow/rpa-tomorrow/blob/master/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

</p>

> The purpose of RPA Tomorrow is to implement a system where the user can write instructions in clear text in order to instruct the computer what to do. This application utilizes natural language processing together with custom-made neural networks in order to parse the intent of the given text and then returns an executable task.

For users of the system there are two user interfaces implemented, a CLI and a GUI.

## Table of contents

1. [Requirements](#requirements)
2. [Setup](#setup)
   1. [Advanced setup](#advanced-setup)
3. [Quickstart](#quickstart)
4. [Usage](#usage)
   1. [CLI](#cli)
   2. [GUI](#gui)
5. [DEMO](#demo)
6. [Documentation](#documentation)
7. [Testing](#testing)
8. [License](#license)

## Requirements

Linux and Windows:

- Python 3+
- Anaconda or Miniconda

Additional for Windows Only:

- Microsoft C++ Build Tools (for GUI)

## Quickstart

1. Follow the [setup](#setup)
2. Start the application through either the [CLI](#cli) or [GUI](#gui)

## Setup

Clone and `cd` into the repository. Create a file named `.env` and inside it declare
the variable `RPA_SECRET=<secret>` where `<secret>` should be replaced by the passphrase
that will be used for deriving the key for encryption and decryption of the password
required for authentication against the SMTP server.

To create and activate the project environment the included setup script can be used
(Linux only)
```bash
$ source init_env.sh
```

Otherwise you can do it manually

```bash
# Create environment
$ conda env create -f rpa-tomorrow.yml
# Install RPA models
$ pip install -r requirements.txt
# Activate environment
$ conda activate rpa-tomorrow
```

**NOTE!** If you're on Windows, replace all `rpa-tomorrow` with `rpa-tomorrow-win` above.

### Advanced setup

- To authenticate with Google for GCal support see [google_auth_setup.md](docs/google_auth_setup.md)
- User settings can be configured manually inside `config/` or through the GUI

## Usage

RPA Tomorrow accepts regular natural text as input. Below is the information for the supported interfaces.
See [accepted_input.md](docs/accepted_input.md) if the program is struggling to understand the input.

### CLI

The CLI can be started as follows

```bash
$ python lib/cli/cli.py
```

Inside the CLI, type `help` for more instructions.

### GUI

The GUI can be started as follows

```bash
$ fbs run
```

## DEMO

[![asciicast](https://asciinema.org/a/NJHkkxjK2dXprr2pV6fb2DXgL.svg)](https://asciinema.org/a/NJHkkxjK2dXprr2pV6fb2DXgL?size=medium&autoplay=true)

## Documentation

Documentation are provided in `docs/` [here](/docs).

## Testing

The tests can be run with the following command

```bash
$ pytest
```

A coverage report will automatically be generated and saved in `htmlcov/` and it can be viewed at `htmlcov/index.html`

## License

Licensed under the MIT license. See [LICENSE](LICENSE) for details.
