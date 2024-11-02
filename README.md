# Netz39 Ampel Controller

> Microservice to provide the Controller for our Traffic Light and Space Status.

This could be done in NodeRed, but it is part of our critical infrastrukture and should
run independently.

## Usage

### Configuration

Configuration is done using environment variables:

* `PORT`: Target port when used with docker-compose (default `8080`)

### Run with Docker

```bash
docker run --rm -it \
    -p 8080:8080 \
    netz39/ampel-controller
```

### Run with Docker-Compose (Development)

To run with [docker-compose](https://docs.docker.com/compose/) copy  [`.env.template`](.env.template) to `.env` and edit the necessary variables. Then start with:

```bash
docker-compose up --build
```

Please note that this compose file will rebuild the image based on the repository. This is helpful during development and not intended for production use.

When done, please don't forget to remove the deployment with
```bash
docker-compose down
```

## Maintainers

* Stefan Haun ([@penguineer](https://github.com/penguineer))


## License

[MIT](LICENSE.txt) © 2024 Netz39 e.V. and contributors
