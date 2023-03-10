import express from 'express'
import { connectToDatabase } from './lib/mongoConnection'
import { Collection, ObjectId } from 'mongodb'
import { User } from '@/types'

const app = express()
app.use(express.json())
const port = 3000

export default async function main() {
  const client = await connectToDatabase()
  const usersCollection = client.db('usersDb').collection<User>('users')

  app.get("/user", async (req, res) => {
    try {
      const users = await usersCollection.find({}).toArray()
      const data = users.map(({ _id, ...rest }) => {
        return {
          ...rest,
          id: _id.toString(),
        }
      })

      res.status(200).json({
        code: 200,
        data: data
      })

    } catch (error) {
      console.error(error)
      res.status(500).json({
        "code": 500,
        "message": "Server unable to get all users",
      })
    }
  })

  app.get("/user/:id", async (req, res) => {
    try {
      const objectId = new ObjectId(req.params.id) // transform the string id into a MongoDB ObjectId
      const result = await usersCollection.findOne({ _id: objectId })
      if (result === null) {
        return res.status(404).json({
          code: 404,
          data: result,
        })
      }

      const user: User = { ...result, id: result._id.toString() }
      res.status(200).json({
        code: 200,
        data: user,
      })

    } catch (error) {
      console.error(error)
      res.status(500).json({
        "code": 500,
        "message": `Server unable to get user id ${req.params.id}`
      })
    }
  })

  app.post("/user", async (req, res) => {
    try {
      const body: User = req.body
      const userExists = await usersCollection.findOne({ email: body.email })
      if (userExists) {
        return res.status(404).json({
          code: 404,
          message: `User email ${body.email} already exists.`,
        })
      }

      const result = await usersCollection.insertOne(body)
      // console.log('result', result)
      res.status(201).json({
        code: 201,
        data: body,
      })


    } catch (error) {
      console.error(error)
      res.status(500).json({
        "code": 500,
        "message": `Server unable to insert user`
      })
    }
  })

  app.put("/user/:id", async (req, res) => {
    try {
      const objectId = new ObjectId(req.params.id)
      const userExists = await usersCollection.findOne({ _id: objectId })
      if (!userExists) {
        return res.status(404).json({
          code: 404,
          message: `User id ${req.params.id} does not exist.`,
        })
      }

      const body: User = req.body
      const result = await usersCollection.updateOne({ _id: objectId }, { $set: body })
      // console.log('result', result)
      res.status(200).json({
        code: 200,
        data: result,
      })


    } catch (error) {
      console.error(error)
      res.status(500).json({
        "code": 500,
        "message": `Server unable to insert user`
      })
    }
  })

  app.delete("/user/:id", async (req, res) => {
    try {
      const objectId = new ObjectId(req.params.id)
      const userExists = await usersCollection.findOne({ _id: objectId })
      if (!userExists) {
        return res.status(404).json({
          code: 404,
          message: `User id ${req.params.id} does not exist.`,
        })
      }

      const result = await usersCollection.deleteOne({ _id: objectId })
      // console.log('result', result)
      res.status(200).json({
        code: 200,
        data: result,
      })

    } catch (error) {
      console.error(error)
      res.status(500).json({
        "code": 500,
        "message": `Server unable to delete user id ${req.params.id}`
      })
    }
  })

  app.listen(port, () => {
    console.log(`Listening on port ${port}`)
  })

}

main()