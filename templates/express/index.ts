// TODO
import { PrismaClient } from ".prisma/client"
import express from "express"

const prisma = new PrismaClient()
const app = express()
const port = 5000

app.get("/", (req, res) => {
	res.send("Hello World!")
})

app.listen(port, () => {
	console.log(`Example app listening on port ${port}`)
})

// route to retrieve users from database
app.get("/users", async (req, res) => {
	const users = await prisma.user.findMany()
	res.json(users)
})
