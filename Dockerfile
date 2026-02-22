FROM ubuntu:15.04
COPY . /app
RUN make /app
CMD python /app/app.py
