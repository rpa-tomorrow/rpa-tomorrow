#!/bin/bash

# Run this from source
black . --line-length=120
flake8 . --max-line-length=120
