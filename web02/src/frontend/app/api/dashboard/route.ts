import { type NextRequest, NextResponse } from "next/server";
import { ObjectId } from "mongodb";
import { getUser } from "@/lib/auth";
import { connectDB } from "@/lib/db";
import { escapeRegex } from "@/lib/utils";

interface Transaction {
  _id: ObjectId;
  receiver: string;
  sender: string;
  amount: number;
  note: string;
  status: string;
}

export async function GET(request: NextRequest) {
  const db = await connectDB();
  try {
    const user = await getUser(request);

    if (!user || !user.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const userId = new ObjectId(String(user.id));
    const { searchParams } = new URL(request.url);
    const filter = searchParams.get("filter")?.trim();

    const value = searchParams.get("value");

    let [balance, transactions] = await Promise.all([
      db.collection("balances").findOne({ _id: userId }),
      db
        .collection("transactions")
        .find({
          $or: [{ sender_id: userId }, { receiver_id: userId }],
        })
        .toArray(),
    ]);

    if (
      filter &&
      value &&
      !filter.startsWith("sender") &&
      !filter.startsWith("receiver")
    ) {
      const regex = new RegExp(`.*${escapeRegex(value)}.*`, "i");
      transactions = await db
        .collection<Transaction>("transactions")
        .find({
          $where: function () {
            let t = Object.fromEntries(
              Object.keys(transactions).map((key) => [key, ""]),
            );

            t.sender = user.username as string;
            t.receiver = user.username as string;

            for (let i = 0; i < transactions.length; i++) {
              if (regex.test(transactions[i].note)) {
                t[filter] = transactions[i].note;
              }
            }
            return this.sender === t.sender && this.receiver === t.receiver;
          },
        })
        .toArray();
    }

    balance = balance?.amount;
    return NextResponse.json({ balance, transactions });
  } catch (error) {
    console.error("Dashboard error:", error);
    return NextResponse.json(
      { error: "An error occurred, please try again" },
      { status: 500 },
    );
  }
}
