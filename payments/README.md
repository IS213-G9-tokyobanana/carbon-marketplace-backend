# Payment Microservice

A Node.js Express Application with MongoDB database.

MongoDB Admin Panel can be accessed through localhost:8888, and the Express App is running on port 5008. 

To create a new PaymentIntent in Stripe, submit a POST request to localhost:5008/payments with params *amount* (in cents) and *currency* (string value like 'sgd' or 'usd'). 

The PaymentIntent object from Stripe will be saved in the local database with the PaymentIntent_Id as the identifier.

# To run the container
1. Load the .env file in the payments folder.
2. Simply docker-compose up.