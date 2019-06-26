# text-blurring

#### Docker for API

You can build and run the docker using the following process:

Cloning
```console
git clone https://github.com/jqueguiner/text-blurring.git text-blurring
```

Building Docker
```console
cd text-blurring && docker build -t tet-blurring -f Dockerfile-api .
```

Running Docker
```console
echo "http://$(curl ifconfig.io):5000" && docker run -p 5000:5000 -d text-blurring
```

Calling the API for image processing
```console
curl -X POST "http://MY_SUPER_API_IP:5000/process" -H "accept: image/png" -H "Content-Type: application/json" -d '{"url":"https://i.ibb.co/CVTS9w3/input.jpg"}' --output blurred_image.png
```
