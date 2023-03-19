import { TransactionInput } from "./types"
import Stripe from "stripe"
import mongoDB, { MongoClient } from "mongodb"

import * as dotenv from "dotenv"
dotenv.config()
import express from "express"

const app = express()
app.use(express.json())
const port = 5000
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
	apiVersion: "2022-11-15",
	typescript: true,
})
const collections: { paymentintents?: mongoDB.Collection } = {}
const database: { db?: mongoDB.Db } = {}

// function to connect to MongoDB
async function connectToDatabase() {
	const client: mongoDB.MongoClient = new MongoClient(
		process.env.DB_CONN_STRING
	)
	await client.connect()

	database.db = client.db(process.env.DB_NAME)
}

connectToDatabase()

async function createCollection() {
	const collection: mongoDB.Collection = database.db.collection(
		process.env.COLLECTION_NAME
	)
	collections.paymentintents = collection
	console.log(
		`Successfully connected to database: ${database.db.databaseName} and collection: ${collections.paymentintents}`
	)
}

createCollection()

app.get("/", (req, res) => {
	res.send("Hello World!")
})

app.listen(port, () => {
	console.log(`Example app listening on port ${port}`)
})

// route to create Payment Intent in Stripe
app.post("/payments", async (req, res) => {
	const input: TransactionInput = req.body

	const params: Stripe.PaymentIntentCreateParams = {
		amount: input.amount,
		currency: input.currency,
		automatic_payment_methods: { enabled: true }, // for the sake of this project, we just assume automatic payment options
	}

	try {
		const paymentIntent: Stripe.PaymentIntent =
			await stripe.paymentIntents.create(params)

		const dbTransaction = {
			payment_id: paymentIntent.id,
			payment_intent: paymentIntent,
			quantity_tco2e: input.quantity_tco2e,
			project_id: input.project_id,
			owner_id: input.owner_id,
			buyer_id: input.buyer_id,
			created_at: new Date(),
			updated_at: new Date(),
		}

		const databaseResult = await collections.paymentintents.insertOne(
			dbTransaction
		)

		await res.send({ clientSecret: paymentIntent.client_secret })
	} catch (e) {
		res.status(400).send({
			error: {
				message: e.message,
			},
		})
	}
})
