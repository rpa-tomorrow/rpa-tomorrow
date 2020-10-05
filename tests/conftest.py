import sys

# This solves an issue with not being able to import modules from the lib/
# folder in the test files
sys.path.append(".")
sys.path.append("..")
