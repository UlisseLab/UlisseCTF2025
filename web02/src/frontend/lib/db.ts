import { MongoClient } from "mongodb"

// MongoDB connection configuration
const MONGO_USER = process.env.MONGO_INITDB_ROOT_USERNAME || "admin"
const MONGO_PASS = process.env.MONGO_INITDB_ROOT_PASSWORD || "password"
const MONGO_HOST = process.env.MONGO_HOST || "mongodb"
const MONGO_DB = process.env.MONGO_INITDB_DATABASE || "stackbank"
const MONGO_URI = `mongodb://${MONGO_USER}:${MONGO_PASS}@${MONGO_HOST}:27017/`

// Database connection singleton
let client: MongoClient | null = null

export async function connectDB() {
  if (client) {
    return client.db(MONGO_DB)
  }

  client = new MongoClient(MONGO_URI)
  await client.connect()
  return client.db(MONGO_DB)
}