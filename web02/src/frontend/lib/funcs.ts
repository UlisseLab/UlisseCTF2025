import { randomBytes } from "crypto"
import { connectDB } from "./db"
import { ObjectId } from "mongodb"

// User management
export async function getUser({ username, password }: { username?: string; password?: string }) {
  const db = await connectDB()

  const query: Record<string, string> = {}
  if (username) query.username = username
  if (password) query.password = password

  return db.collection("users").findOne(query)
}

export async function createUser({ username, password }: { username: string; password: string }) {
  const db = await connectDB()

  const existingUser = await db.collection("users").findOne({ username: username })
  if (existingUser) {
    throw new Error("User already exists")
  }

  const result = await db.collection("users").insertOne({
    username: username,
    password: password,
  })

  await db.collection("balances").updateOne(
    { _id: new ObjectId(result.insertedId.toString()) }, 
    { $set: { amount: 100 } }, 
    { upsert: true }
  )

  return result
}

export async function getUserById(id: string) {
  const db = await connectDB()
  return db.collection("users").findOne({ _id: new ObjectId(id) })
}

export async function getUserByUsername(username: string) {
  const db = await connectDB()
  const result = await db.collection("users").findOne({ username })
  return result ? result._id.toString() : null
}

// Balance management
export async function setBalance({ id, balance }: { id: string; balance: number }) {
  const db = await connectDB()

  await db.collection("balances").updateOne({ _id: new ObjectId(id) }, { $set: { amount: balance } }, { upsert: true })

  return true
}

export async function getBalance({ id }: { id: string }) {
  const db = await connectDB()
  const balance = await db.collection("balances").findOne({ _id: new ObjectId(id) })
  return balance ? balance.amount : 0
}

// Transaction management
export async function getTransactions(id: string) {
  const db = await connectDB()

  const transactions = await db
    .collection("transactions")
    .find({
      $or: [{ send_id: new ObjectId(id) }, { recv_id: new ObjectId(id) }],
    })
    .toArray()

  return transactions
}

export async function addTransaction(userId: string, amount: number, description: string) {
  const db = await connectDB()

  const transaction = {
    userId: new ObjectId(userId),
    amount,
    description,
    date: new Date(),
  }

  await db.collection("transactions").insertOne(transaction)
  return transaction
}

// Admin initialization
export async function initializeAdmin() {
  const password = process.env.ADMIN_PASS || randomBytes(32).toString("hex")

  try {
    const admin = await createUser({
      username: "administrator",
      password: password,
    })

    await setBalance({
      id: admin.insertedId.toString(),
      balance: 1000,
    })

    console.log(`Administrator account created with password: ${password}`)
    return { username: "administrator", password }
  } catch (error) {
    console.log("Admin already exists")
    return null
  }
}