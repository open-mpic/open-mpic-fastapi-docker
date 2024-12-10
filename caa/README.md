# caa

## Development

Instructions for developing the open-mpic caa service.

### Getting Started

If using the devcontainer, you already have the required tools installed.

Run the following commands to get started:

```bash
# Install the python version specified in the .python-version file
pyenv install
# Activate the python version specified in the .python-version file
pyenv activate
# Install the dependencies
pip install -r requirements.txt
# Start the service
fastapi dev
```