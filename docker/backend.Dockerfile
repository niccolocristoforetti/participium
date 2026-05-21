FROM python:3.12-slim

WORKDIR /usr/src/app

COPY src/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend/ ./

EXPOSE 5050

CMD ["flask", "--app", "wsgi:app", "run", "--host", "0.0.0.0", "--port", "5050", "--without-threads"]
