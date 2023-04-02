import { DbTransactionOutput, TransactionInput } from "./types"
import Stripe from "stripe"
import mongoDB, { MongoClient } from "mongodb"

import * as dotenv from "dotenv"
dotenv.config()
import express from "express"

const app = express()
app.use((req, res, next) => {
	if (req.originalUrl === "/webhooks") {
		next()
	} else {
		express.json()(req, res, next)
	}
})
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

	const db = client.db(process.env.DB_NAME)

	const collection: mongoDB.Collection = db.collection(
		process.env.COLLECTION_NAME
	)
	collections.paymentintents = collection
	console.log(
		`Successfully connected to database: ${db.databaseName} and collection: ${collections.paymentintents}`
	)
}

connectToDatabase()

app.get("/", (req, res) => {
	res.send("Hello World!")
})

app.listen(port, () => {
	console.log(`Example app listening on port ${port}`)
})

// route to get Payment Intent saved in MongoDB
app.get("/payments", async (req, res) => {
	const input: string = req.query.paymentid

	try {
		const result = await collections.paymentintents.findOne({
			$or: [{ payment_id: input }],
		})
		if (result) {
			res.send({ success: true, data: { paymentIntent: result } })
		} else {
			res.send({
				success: false,
				data: { message: "No payment intent with that ID found." },
			})
		}
	} catch (e) {
		res.status(400).send({
			success: false,
			data: { message: e.message },
		})
	}
})

// route to create Payment Intent in Stripe
app.post("/payments", async (req, res) => {
	const input: TransactionInput = req.body
	let paymentIntent: Stripe.PaymentIntent
	let dbTransaction: DbTransactionOutput

	const params: Stripe.PaymentIntentCreateParams = {
		amount: input.amount,
		currency: input.currency,
		automatic_payment_methods: { enabled: true }, // for the sake of this project, we just assume automatic payment options
	}

	try {
		paymentIntent = await stripe.paymentIntents.create(params)
	} catch (e) {
		res.status(400).send({
			success: false,
			data: {
				message: e.message,
				resource: {
					amount: input.amount,
					currency: input.currency,
				},
			},
		})
	}

	try {
		dbTransaction = {
			payment_id: paymentIntent.id,
			payment_intent: paymentIntent,
			quantity_tco2e: input.quantity_tco2e,
			milestone_id: input.milestone_id,
			owner_id: input.owner_id,
			buyer_id: input.buyer_id,
			created_at: new Date(),
			updated_at: new Date(),
		}

		collections.paymentintents.insertOne(dbTransaction)

		res.send({ success: true, data: paymentIntent.client_secret })
	} catch (e) {
		res.status(400).send({
			success: false,
			data: {
				message: e.message,
				resource: dbTransaction,
			},
		})
	}
})

// route to receive webhooks from Stripe
app.post(
	"/webhooks",
	express.raw({ type: "application/json" }),
	async (req, res) => {
		const sig = req.headers["stripe-signature"]

		let event

		try {
			event = stripe.webhooks.constructEvent(
				req.body,
				sig,
				process.env.STRIPE_ENDPOINT_SECRET
			)
		} catch (err) {
			console.log(err.message)
			res.status(400).send(`Webhook Error: ${err.message}`)
			return
		}

		switch (event.type) {
			case "charge.succeeded":
				const charge = event.data.object
				console.log(charge)
			case "payment_intent.created":
				const paymentIntent = event.data.object
				console.log(paymentIntent)
			case "payment_intent.succeeded":
				const paymentIntentStatus = event.data.object
				console.log(paymentIntentStatus)
				break
			case "payment_method.attached":
				const paymentMethod = event.data.object
				console.log(paymentMethod)
				break
			default:
				console.log(`Unhandled event type ${event.type}`)
		}

		res.send({ received: true })

		// if (req.body) {
		// 	res.send({ success: true, data: req.body })
		// } else {
		// 	res.status(400).send({
		// 		success: false,
		// 		data: {
		// 			message: "No message received.",
		// 		},
		// 	})
		// }
	}
)
