# Express + Prisma Template

Steps:
1. Retrieve the .env file for the database URL (or manually enter).

2. Create the docker container for the postgresql database.
This is done by ```docker compose up```, in templates/dockerfiles/prisma-postgres.

3. Migrate the database schema from /express/prisma/schema.prisma
Run ```npx prisma migrate dev --name init``` from /express/prisma.

4. You may refer to postgrestest.ts in templates/express/prisma/dist for some sample code on creating the Prisma Client queries - creating an instance of an entity and also getting instances.
To run this code, cd to the /express/prisma/dist folder, and run ```npx ts-node postgrestest.ts```. This will create a sample user in the database.

5. You can run the Express app. 
Locate the file in templates/express/, then run the two commands ```npm run build``` and ```npm run start```.
The Prisma Function getAllUsers is in localhost:5000/users, and will return the user created in postgrestest.ts.