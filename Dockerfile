FROM ubuntu:15.04
COPY . /app
RUN make /app
EXPOSE 5001:5001
CMD python3 /app/app.py
