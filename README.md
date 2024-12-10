# open-mpic-container
A Fast API wrapper for the Open MPIC in docker containers.

## Development

Instructions for developing the open-mpic services.

### Devcontainers

This repository contains a `.devcontainer` folder containing a `devcontainer.json` that can be used to develop open-mpic services. 

Refer to the [Visual Studio Code Remote - Containers](https://code.visualstudio.com/docs/remote/containers) documentation for more information on how to use devcontainers.

### Getting Started

Once you have opened the repository in a devcontainer, and it builds for the first time, close the terminal and reopen it to ensure that the environment is set up correctly and tools such as `pyenv` are available in the PATH.

Once your environment is setup, change to the directory of the service you want to work on and run the following commands:

```bash
# Change to the directory of the service you want to work on
cd coordinator
# Install the python version specified in the .python-version file
pyenv install
# Activate the python version specified in the .python-version file
pyenv activate
# Install the dependencies
pip install -r requirements.txt
# Start the service
fastapi dev
```
