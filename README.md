# My diploma project

To generate the code:
```
./generate.sh
```

To launch the client grpcui:
```
grpcui -plaintext localhost:your_value
```

## Run client

To show help message of client run next command:
```
python client.py -h
```

To run client with default params:
```
python client.py
```

## Run server

Before run server run the following commands:
- Set the virtual variables required to connect to the database in the file `server.env` (`DB_NAME`, `DB_USER`, `DB_PASSWORD`).
- Create a folder named `./ssl`. Generate self-signed keys and put them in this folder.

### Run locally

Firstly, you need to deploy your database.

- Install the dependencies described in the file `requirements.txt`.
- Generate the code with the next command:
    ```
    ./generate.sh
    ```
- Start the server using the command:
    ```
    python server.py
    ```

### Run with docker

Firstly, you need to deploy your database.

- Build the docker image with the next command:
    ```
    docker build . -t your-image-name
    ```
- Run container using the command:
    ```
    docker run --env-file server.env -p 50051:50051 -p 50052:50052 --name your_container_name your-image-name
    ```
    

### Run with docker-compose

- Pull the PostgreSQL image from [DockerHub](https://hub.docker.com/_/postgres). The current version of project uses a postgres [image v17.2](https://hub.docker.com/layers/library/postgres/17.2/images/sha256-a6d9276e20b3b89a6e86d0201120235eea310a283ba12e22b9a0dc2f8b368346).
- Build a server image using the command
    ```
    docker build . -t your-image-name
    ```
- Assign variables to `db.env` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`). These values must correspond to the `server.env` (`DB_USER`, `DB_PASSWORD`, `DB_NAME`)
- Run the project with the next command:
    ```
    docker-compose up
    ```
