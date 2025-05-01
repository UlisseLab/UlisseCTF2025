# StackBank1

|         |                            |
| ------- | -------------------------- |
| Authors | Alan Davide Bovo <@AlBovo> |
| Points  | 500                        |
| Tags    | web                        |

## Challenge Description

This bank🏦 will let you ~~legally~~ launder your dirty money, so you can live the high life in Dubai 🤑.

Give it a try — for now, it only lets you send and receive money for your oh-so-reputable _Ponzi_ scheme💸.

Bank's website: [http://stackbank.challs.ulisse.ovh:7723/](http://stackbank.challs.ulisse.ovh:7723/)

## Overview

**Stack Bank** is a web application that allows users to perform typical banking operations such as transferring money to other users or sending funds directly to the **administrator** of the service.

After initiating a transaction, users are required to wait up to **10 seconds** for the operation to complete. This delay is due to an internal **bot** that asynchronously verifies the transaction's values and integrity before marking it as successful.

However, there is one exception: **transactions sent to the administrator** are immediately marked as successful, without undergoing any verification or integrity check.

## Analysis

The challenge provides multiple services behind an `nginx` reverse proxy configured as follows:

```nginx
location /service/ {
    proxy_pass http://backend:4000/;
    ...
}

location / {
    proxy_pass http://frontend:3000;
    ...
}
```

The **frontend** is a web application built with **Next.js**, while the **backend** is a **Flask** application that exposes various functionalities. Notably, the backend integrates with native C code via **CTypes**, using a shared object library called `libackend.so` to implement some of its core logic.

The first flag is inserted into the **MongoDB** database during the backend's initialization phase.
It is stored as part of a **transaction** where both the **sender** and the **receiver** are set to the `administrator` user.

## Vulnerabilities

Since the flag can be found inside the transaction involving the administrator, it may be useful to analyze the endpoint provided in the frontend, located at `app/api/dashboard/route.ts`. This file implements the following code:

```ts
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
```

This function is **vulnerable** because an attacker can manipulate the provided values in such a way that both the **sender** and **receiver** are set to `administrator`, thus retrieving the **admin transaction** containing the flag.

The vulnerability arises due to **prototype pollution**, which is possible because of this code:

```ts
t[filter] = transactions[i].note;
```

An attacker could craft a payload like:

- **filter**: `__proto__`
- **transaction note**: `{'a': 'b'}`

This would cause the `t` object to gain an additional property (`a`) due to prototype pollution, effectively making `t.a = 'b'`. As a result, the attacker can manipulate the object in ways that bypass the intended functionality and access restricted data, such as the flag.

The final piece required to exploit this challenge can be found in the `/service/transaction` endpoint in the backend:

```python
@app.route('/transaction', methods=['POST'])
@login_required
def transaction(user):
    ...
    # validation checks on the value omitted for brevity

    if receiver['username'] == 'administrator':
        return invest(user)

    ...

# The following route is no longer used...
# @app.route('/invest', methods=['POST'])
# @login_required
def invest(user):
    amount = request.json['amount']
    note = request.json['note']

    mongo.db.balances.update_one(
        {"user_id": user[0]},
        {"$inc": {"amount": -amount}}
    )

    mongo.db.transactions.insert_one({
        'sender_id': user[0],
        'sender': user[1],
        'receiver_id': mongo.db.users.find_one({'username': 'administrator'})['_id'],
        'receiver': 'administrator',
        'amount': amount,
        'note': note,
        'status': 'success'
    })

    return jsonify({'message': 'Investment added'}), 200
```

An attacker can exploit the system by sending funds directly to the `administrator` account, which triggers the `invest` function that allows the attacker to set their own `note` field (e.g., `{'sender': 'administrator', 'receiver': 'administrator'}`).

## Unintended Solutions

I sincerely apologize for any unintended solutions that may have unintentionally oversimplified the challenge, such as sending payloads like `filter= sender&value=a` or `filter=^&value=a` (that leaked all the database transactions). Moving forward, I promise to conduct more thorough testing on my future challenges to ensure the best possible experience for participants next year **`ᕙ(  •̀ ᗜ •́  )ᕗ`**
