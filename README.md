# DockerHomework22Feb2026
homework - docker 1

docker build -t myApp:1.0.0 .


docker run -p 80:5001 -itd --name myApp [xxxImageNamexxx]


or docker run -e AWS_ACCESS_KEY_ID=your_key \
           -e AWS_SECRET_ACCESS_KEY=your_secret \
           -e AWS_REGION=us-east-1 \
           myimage
