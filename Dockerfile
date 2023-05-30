FROM python:3.8.10

RUN pip install --upgrade pip && pip install --upgrade setuptools

RUN apt update && \
    apt install -y build-essential && \
    apt install -y && \
    apt install -y libpoppler-cpp-dev && \
    apt install -y pkg-config python3-dev

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["streamlit", "run", "home.py"]
