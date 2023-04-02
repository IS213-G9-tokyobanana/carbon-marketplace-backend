# Payment Microservice

A Node.js Express Application with MongoDB database.

Use Mongo Compass as an explorer for the mongodb, and access via ```mongodb://{username}:{password}@localhost:27017```.

To create a new PaymentIntent in Stripe, submit a POST request to localhost:3000/payments with the following paramaters in the body.
```
    amount: number
	currency: string
	quantity_tco2e: number
	project_id: string
	owner_id: string
	buyer_id: string
```

The PaymentIntent object from Stripe will be saved in MongoDB with the PaymentIntent_Id as the identifier, and other necessary fields.

To retrieve previously created and saved Payment Intents, submit a GET request to localhost:3000/payments with a paymentid query. You will receive one saved transaction with the same payment_id.

To test webhooks (temporary while pending deployment):
You need my Stripe account and the CLI but the link with instructions is here: 
https://dashboard.stripe.com/test/webhooks/create?endpoint_location=local

# To run the container
1. Load the .env file in the payments folder.
2. Simply docker-compose up.