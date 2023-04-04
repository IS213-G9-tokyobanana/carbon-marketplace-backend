import { DbTransactionOutput, TransactionInput } from "./types";
import { config } from "dotenv";
import { MongoClient, Collection } from "mongodb";
import express from "express";

config();

const app = express();
app.use(express.json());
app.use(function (err, req, res, next) {
  // error handling middleware
  console.error(err.stack);
  res.status(500).send({
    success: false,
    data: {
      message: err.message,
    },
  });
});
app.use(function (req, res, next) {
  // logging middleware
  console.log(`${new Date().toISOString()} - ${req.method} ${req.originalUrl}`);
  next();
});

const port = 5000;

const collections: { payments?: Collection } = {};

// function to connect to MongoDB
async function connectToDatabase() {
  const client: MongoClient = new MongoClient(process.env.DB_CONN_STRING);
  await client.connect();

  const db = client.db(process.env.DB_NAME);

  const collection: Collection = db.collection(process.env.COLLECTION_NAME);
  collections.payments = collection;
  console.log(
    `Successfully connected to database: ${db.databaseName} and collection: ${collections.payments}`
  );
}

app.get("/", (req, res) => {
  res.send("Payments microservice healthy");
});

// route to get Payment Intent saved in MongoDB
app.get("/payments", async (req, res) => {
  let input;
  let result;
  if (req.query.payment_id) {
    input = req.query.payment_id;
    console.log(`Query payment id: ${input} `);
  } else {
    input = req.query.milestone_id;
    console.log(`Query milestone id: ${input} `);
  }

  try {
    if (req.query.payment_id) {
      result = await collections.payments.findOne({
        $or: [{ payment_id: input }],
      });
    } else {
      result = await collections.payments.findOne({
        $or: [{ milestone_id: input }],
      });
    }

    if (result) {
      res.status(200).send({ success: true, data: result });
    } else {
      res.status(404).send({
        success: false,
        data: { message: "No payment intent with that ID found." },
      });
    }
  } catch (e) {
    res.status(400).send({
      success: false,
      data: { message: e.message },
    });
  }
});

// route to create Payment Intent in Stripe
app.post("/payments", async (req, res) => {
  const input = req.body;

  try {
    const dbTransaction = {
      payment_id: input.payment_id,
      quantity_tco2e: input.quantity_tco2e,
      project_id: input.project_id,
      milestone_id: input.milestone_id,
      owner_id: input.owner_id,
      buyer_id: input.buyer_id,
      created_at: new Date(),
      updated_at: new Date(),
    } as DbTransactionOutput;

    collections.payments.insertOne(dbTransaction);

    res.status(201).send({ success: true, data: dbTransaction });
  } catch (e) {
    res.status(400).send({
      success: false,
      data: {
        message: e.message,
        resource: input,
      },
    });
  }
});

connectToDatabase();

app.listen(port, () => {
  console.log(`Payments MS listening on port ${port}`);
});
