# What's this ?
This is a messaging server written in Python using AsyncIO and Websocket:
if A sends a message M to B and B is known by the service, the service should
deliver M to B.

## Requirements
* Python 3.5 (this project uses the new "async/await" keywords)
* Tox

## Run
To launch the program in a virtualenv, just do
```console
tox -e run
```

Then open *client.html* in your favorite web browser and start sending
messages like it's Saturday night.

## Test
To run the unit tests in a virtualenv, just do
```console
tox -e py35
```

## Lint
To run the code linter, just do
```console
tox -e lint
```

## Coverage
To measure code coverage, just do
```console
tox -e coverage
```
