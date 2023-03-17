// TODO
import { PrismaClient } from ".prisma/client"
import { TransactionInput } from "./types"
import Stripe from "stripe"
import mongoDB, { MongoClient } from "mongodb"

import * as dotenv from "dotenv"
dotenv.config()
import express from "express"

const prisma = new PrismaClient()
const app = express()
const port = 5000
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
	apiVersion: "2022-11-15",
	typescript: true,
})
const collections: { paymentintents?: mongoDB.Collection } = {}

// function to connect to MongoDB
async function connectToDatabase() {
	const client: mongoDB.MongoClient = new MongoClient(
		process.env.DB_CONN_STRING
	)
	await client.connect()

	const db: mongoDB.Db = client.db(process.env.DB_NAME)
	const collection: mongoDB.Collection = db.collection(
		process.env.COLLECTION_NAME
	)
	collections.paymentintents = collection
	console.log(
		`Successfully connected to database: ${db.databaseName} and collection: ${collections.paymentintents}`
	)
}

app.get("/", (req, res) => {
	res.send("Hello World!")
})

app.listen(port, () => {
	console.log(`Example app listening on port ${port}`)
})

// route to create Payment Intent in Stripe
app.post("/payment", async (req, res) => {
	const input: TransactionInput = req.query

	const params: Stripe.PaymentIntentCreateParams = {
		amount: input.amount,
		currency: input.currency,
		automatic_payment_methods: { enabled: true }, // for the sake of this project, we just assume automatic payment options
	}

	connectToDatabase()

	try {
		const paymentIntent: Stripe.PaymentIntent =
			await stripe.paymentIntents.create(params)

		const request = {
			paymentId: paymentIntent.id,
			paymentIntent: paymentIntent,
		}

		const databaseResult = await collections.paymentintents.insertOne(
			request
		)

		// check the database result status
		console.log(databaseResult)

		const result = await res.send({
			clientSecret: paymentIntent.client_secret,
		})
	} catch (e) {
		res.status(400).send({
			error: {
				message: e.message,
			},
		})
	}
})
