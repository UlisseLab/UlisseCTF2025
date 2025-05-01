/** Not part of the challenge. It automatically computes the proof of work for you */
const buttons = document.querySelectorAll(".share-btn")

buttons.forEach(button =>
    button.addEventListener("click", async (event) => {
        const postId = button.dataset.postId;
        if (!postId) {
            console.error("Missing PostId to share");
            return;
        }
        const originalHtml = button.innerHTML;
        // Disable button & show spinner
        buttons.forEach(button => button.setAttribute("disabled", 1));
        button.querySelector("i").remove()
        button.innerHTML += `
                <div class="preloader-wrapper small active">
                    <div class="spinner-layer spinner-blue-only">
                        <div class="circle-clipper left">
                            <div class="circle"></div>
                        </div>
                        <div class="gap-patch">
                            <div class="circle"></div>
                        </div>
                        <div class="circle-clipper right">
                            <div class="circle"></div>
                        </div>
                    </div>
                </div>
            `;

        M.toast({ html: "Computing PoW... Please wait ~10/20s", displayLength: 5 * 1000 });
        try {
            // Fetch the PoW challenge from the backend
            let resp = await fetch("/get-challenge", {
                method: "POST"
            })

            const data = await resp.json()

            if (!resp.ok) {
                throw Error(data?.msg || "Unknown error")
            }

            const { challenge, difficulty } = data;


            const { nonce } = await process(challenge, difficulty)

            resp = await fetch(`/posts/share/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ nonce })
            })

            if (!resp.ok) {
                throw Error(data?.msg || "Unknown error")
            }

            M.toast({ html: "Admin is visiting your post!", displayLength: 5 * 1000 })

        } catch (err) {
            err => M.toast({ html: `Error "${err}" please refresh and try again`, displayLength: 2000 })
        } finally {
            buttons.forEach(button => button.removeAttribute("disabled"));
            button.innerHTML = originalHtml;
        }
    })
);


// PoW Computation Function
function processTask() {
    return function () {
        // SHA-256 Hashing Function
        function sha256(str) {
            return crypto.subtle.digest("SHA-256", new TextEncoder().encode(str))
                .then(hashBuffer => {
                    let hashArray = Array.from(new Uint8Array(hashBuffer));
                    return hashArray.map(b => b.toString(2).padStart(8, "0")).join(""); // Convert the digest to binary string
                });
        }

        addEventListener('message', async (event) => {
            let data = event.data.data;
            let difficulty = event.data.difficulty;

            let hash;
            let nonce = 0n;
            const difficultyPrefix = '0'.repeat(difficulty);
            do {
                nonce += 1n;
                hash = await sha256(data + nonce);
            } while (hash.substring(0, difficulty) !== difficultyPrefix);
            nonce = String(nonce)
            postMessage({
                nonce,
                data,
                difficulty
            });
        });
    }.toString();
}

function process(data, difficulty = 5) {
    return new Promise((resolve, reject) => {
        let webWorkerURL = URL.createObjectURL(new Blob([
            '(', processTask(), ')()'
        ], { type: 'application/javascript' }));

        // Create WebWorker
        let worker = new Worker(webWorkerURL);

        worker.onmessage = (event) => {
            worker.terminate();
            resolve(event.data);
        };

        worker.onerror = (event) => {
            worker.terminate();
            reject();
        };

        // Execute WebWorker Task
        worker.postMessage({
            data,
            difficulty
        });

        // Destroy URL Object
        URL.revokeObjectURL(webWorkerURL);
    });
}