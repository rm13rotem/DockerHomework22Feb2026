FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN  pip install flask
EXPOSE 5001
CMD python3 app.py
