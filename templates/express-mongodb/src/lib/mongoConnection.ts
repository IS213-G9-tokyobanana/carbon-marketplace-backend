import { MongoClient } from "mongodb"
import * as dotenv from 'dotenv'

// interface User {
//   id: string
//   name: string
// }

// export const collections: { users?: Collection<User> } = {};

export async function connectToDatabase() {
  // Pulls in the .env file so it can be accessed from process.env. No path as .env is in root, the default location
  dotenv.config();
  if (!process.env['MONGODB_URI']) {
    throw new Error('Invalid/Missing environment variable: "MONGODB_URI"')
  }

  try {
    const client = new MongoClient(process.env['MONGODB_URI']);
    console.log(
      `Successfully connected to mongodbURI`,
    );
    return client

  } catch (error) {
    console.error("Database connection failed", error);
    process.exit();
  }
  
}



