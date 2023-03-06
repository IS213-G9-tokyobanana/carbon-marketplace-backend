# Express + Prisma Template

First of all, create the docker container for the postgresql database.
This is done by ```docker compose up```, in templates/dockerfiles/prisma-postgres.
You may refer to postgrestest.ts in templates/express/prisma/dist for some sample code on creating the Prisma Client queries - creating an instance of an entity and also getting instances.

Next, you can run the Express app. Locate the file in templates/express/, then run the two commands ```npm run build``` and ```npm run start```.
The Prisma Function getAllUsers is in localhost:5000/users, and will return the user created in postgrestest.ts.