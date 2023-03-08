# Express MongoDB Docker Template
This template is a starting point for building a REST API with Express and MongoDB.

## Prerequisites
Install dependencies
```
npm install
```

Create a `.env` file in the root directory and add the following environment variables
```
# uncomment below if local development using `npm run dev` with mongodb in docker container
MONGODB_URI=mongodb://tokyobanana:naganohara@localhost:27017/users?authSource=admin

# Uncomment below if using docker-compose
# MONGO_INITDB_ROOT_USERNAME=tokyobanana
# MONGO_INITDB_ROOT_PASSWORD=naganohara
# MONGODB_URI=mongodb://tokyobanana:naganohara@mongo:27017/users?authSource=admin
```

---
3 ways to run the server with MongoDB
1. Local development using `npm run dev`
2. Using `docker run`
3. Using `docker-compose`

## Local development using `npm run dev`
Starting mongodb container for the first time
```
docker run --name mongo -p 27017:27017 --mount 'type=volume,src=mongo-data,dst=/data/mongodb' -e MONGO_INITDB_ROOT_USERNAME=tokyobanana -e MONGO_INITDB_ROOT_PASSWORD=naganohara mongo
```

Start the server
```
npm run dev
```

Test with Postman by importing the `express-mongodb.postman_collection.json` file in the root directory into Postman. Replace the id accordingly in the relevant API endpoints e.g. GET by id, PUT, DELETE

Stopping mongodb container 
```
docker stop mongo
```

Starting mongodb container subsequently (data is retrieved from volume)
```
docker start mongo
```

## Using `docker run` with mongodb and user container
Build the user container image
```
docker build -t tokyobanana/user:1.0 .
```

Create a network for the containers
```
docker network create mongo-network
```

Starting mongodb container for the first time
```
docker run --name mongo -p 27017:27017 --mount 'type=volume,src=mongo-data,dst=/data/mongodb' --network mongo-network -e MONGO_INITDB_ROOT_USERNAME=tokyobanana -e MONGO_INITDB_ROOT_PASSWORD=naganohara mongo
```

Starting user container
```
docker run --name user -p 3000:3000 --network mongo-network -e MONGODB_URI=mongodb://tokyobanana:naganohara@mongo:27017/users?authSource=admin tokyobanana/user:1.0
```

Test with Postman by importing the `express-mongodb.postman_collection.json` file in the root directory into Postman. Replace the id accordingly in the relevant API endpoints e.g. GET by id, PUT, DELETE

Stopping mongodb container and user container
```
docker stop mongo user
```

Starting mongodb container and user subsequently (data is retrieved from volume)
```
docker start mongo user
```

### Tear down
Removing the stopped mongo container, network and volume
```
docker rm mongo
docker network rm mongo-network
docker volume rm mongo-data
```


## Using `docker-compose`
Uncomment the relevant environment variables in the `.env` file

```
docker-compose up
```

Test with Postman by importing the `express-mongodb.postman_collection.json` file in the root directory into Postman. Replace the id accordingly in the relevant API endpoints e.g. GET by id, PUT, DELETE

Stopping the compose containers
```
docker-compose stop
```

Starting the compose containers subsequently (data is retrieved from volume)
```
docker-compose start
```

Remove all containers, networks and volumes in the docker compose
```
docker-compose down -v
```

