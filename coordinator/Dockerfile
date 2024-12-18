# Set default python version
ARG PYTHON_VERSION=3.11.9

FROM python:${PYTHON_VERSION} AS builder

# Set the working directory for subsequent instructions
WORKDIR /code

# Copy requirements.txt into the container
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

FROM python:${PYTHON_VERSION}

WORKDIR /code

# Set the site-packages path using a RUN instruction
RUN SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")

# Copy site-packages and /usr/local/bin from the builder stage
COPY --from=builder $SITE_PACKAGES $SITE_PACKAGES
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./app /code/app

EXPOSE 80

CMD ["fastapi", "run", "app/main.py", "--proxy-headers",  "--port", "80"]
