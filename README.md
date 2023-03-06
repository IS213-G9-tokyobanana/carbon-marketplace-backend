# Carbon Offset Marketplace

Our app is a platform for companies any entity to (1) obtain funding for new green projects and (2) further monetise existing green projects that have already began consistently removing CO2 from environment.

The focus is primarily on the voluntary market where anyone can fund new projects or support existing projects by buying carbon credits sold by these companies.

We are not focusing on compliance market to facilitate the trading of carbon credits b/w companies who have hit their carbon credit cap set by govt and want to buy carbon credits from other companies with surplus carbon credits (companies whose carbon credits are below the cap set by govt).

# Express + Prisma Template

First of all, create the docker container for the postgresql database.
This is done by ```docker compose up```, in templates/dockerfiles/prisma-postgres.
You may refer to postgrestest.ts in templates/express/prisma/dist for some sample code on creating the Prisma Client queries - creating an instance of an entity and also getting instances.

Next, you can run the Express app. Locate the file in templates/express/, then run the two commands ```npm run build``` and ```npm run start```.
The Prisma Function getAllUsers is in localhost:5000/users, and will return the user created in postgrestest.ts.