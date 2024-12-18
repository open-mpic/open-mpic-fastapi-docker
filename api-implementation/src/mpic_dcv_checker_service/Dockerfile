# Set default python version
ARG PYTHON_VERSION=3.11.9

FROM python:${PYTHON_VERSION}

# Set the working directory for subsequent instructions
WORKDIR /code

# Copy requirements.txt into the container
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

WORKDIR /code

COPY ./app /code/app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
