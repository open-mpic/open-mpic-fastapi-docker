# (Example: For CAA Checker)
# docker build -t mpiccaachecker --build-arg SERVICE_DIR = mpic_caa_checker_service .

# Add args for Python verion (has default) and specific service to build
ARG PYTHON_VERSION=3.11.9

FROM python:${PYTHON_VERSION}
ARG SERVICE_DIR

RUN echo "building service form path: src/${SERVICE_DIR}"

RUN python -m pip install hatch

# Set the working directory for subsequent instructions
WORKDIR /${SERVICE_DIR}

# Copy specific service code and common toml into the container
COPY src/${SERVICE_DIR}/app ./app
COPY pyproject.toml .
RUN hatch dep show requirements > ./app/requirements.txt && python -m pip install --extra-index-url https://test.pypi.org/simple/ -r ./app/requirements.txt
EXPOSE 80

# FIXME uncomment this... for now just debugging stuff...
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
CMD ["sh"]