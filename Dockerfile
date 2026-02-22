FROM python:alpine
COPY . /app
RUN make /app
EXPOSE 80:5001
CMD python3 /app/app.py
