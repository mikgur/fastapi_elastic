FROM python:3.10.5-slim

RUN mkdir /app

COPY . app/

WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry==1.1.13
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]