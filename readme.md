# The Simplest Mail Protocol

## Install
Run :
```bash
git clone https://github.com/prankapple/TSME.git TSME
cd TSME
pip install -r requirements.txt
```

Change the **.env** file and set RUN_KEY as your secret password that will be used to let only you send mesages to EMAIL and
the URL_END like how you want your emails to end (eg. %example.com)

```bash
py server/server.py

```

## Usage
You can use https://tsme.onrender.com as the API_URL but it will be with the 
```env
RUN_KEY=oGUG02~^?5FIYxsMn~5
```

and 

```env
URL_END=$prankapple.github.io/TSME
```
Site example:
```javascript
const API_URL = "http://192.168.0.136:5000"; // Flask server
const RUN_KEY = "my_super_secret_key"; // hardcoded RUN_KEY

let userEmail = "";
let userKey = "";

    function showRegister() {
        document.getElementById("loginDiv").style.display = "none";
        document.getElementById("registerDiv").style.display = "block";
    }

    function showLogin() {
        document.getElementById("registerDiv").style.display = "none";
        document.getElementById("loginDiv").style.display = "block";
    }

    function login() {
        userEmail = document.getElementById("email").value;
        userKey = document.getElementById("key").value;

        if (!userEmail || !userKey) {
            alert("Enter email and password!");
            return;
        }

        fetch(`${API_URL}/inbox`, {
            method: "GET",
            headers: {
                "X-API-KEY": RUN_KEY,
                "X-USER-EMAIL": userEmail,
                "X-USER-KEY": userKey
            }
        }).then(res => {
            if (res.status === 403) {
                alert("Invalid credentials!");
                return;
            }
            document.getElementById("loginDiv").style.display = "none";
            document.getElementById("mailDiv").style.display = "block";
            loadInbox();
        }).catch(err => alert("Server not reachable"));
    }

    function logout() {
        userEmail = "";
        userKey = "";
        document.getElementById("loginDiv").style.display = "block";
        document.getElementById("mailDiv").style.display = "none";
    }

    function registerAccount() {
        const username = document.getElementById("regUsername").value;
        const password = document.getElementById("regPassword").value;

        if (!username || !password) {
            alert("Username and password required");
            return;
        }

        fetch(`${API_URL}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-KEY": RUN_KEY
            },
            body: JSON.stringify({ username, password })
        })
        .then(res => res.json())
        .then(data => {
            if(data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Account created! Your password is also your key.");
                showLogin();
                document.getElementById("email").value = data.email;
                document.getElementById("key").value = data.key;
            }
        }).catch(err => alert("Server not reachable"));
    }

    function sendMessage() {
        const recipient = document.getElementById("recipient").value;
        const subject = document.getElementById("subject").value;
        const body = document.getElementById("body").value;

        if (!recipient || !body) {
            alert("Recipient and message required!");
            return;
        }

        fetch(`${API_URL}/send_email`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-KEY": RUN_KEY,
                "X-USER-EMAIL": userEmail,
                "X-USER-KEY": userKey
            },
            body: JSON.stringify({ recipient, subject, body })
        })
        .then(res => res.json())
        .then(data => {
            if(data.error) alert("Error: " + data.error);
            else {
                alert("Message sent!");
                document.getElementById("recipient").value = "";
                document.getElementById("subject").value = "";
                document.getElementById("body").value = "";
                loadInbox();
            }
        });
    }

    function loadInbox() {
        fetch(`${API_URL}/inbox`, {
            headers: {
                "X-API-KEY": RUN_KEY,
                "X-USER-EMAIL": userEmail,
                "X-USER-KEY": userKey
            }
        })
        .then(res => res.json())
        .then(data => {
            const inboxDiv = document.getElementById("inbox");
            inboxDiv.innerHTML = "";
            data.forEach(mail => {
                const div = document.createElement("div");
                div.classList.add("message");
                div.innerHTML = `<div class="from">From: ${mail.from}</div>
                                 <div class="subject">Subject: ${mail.subject}</div>
                                 <div>${mail.body}</div>
                                 <small>${mail.timestamp}</small>`;
                inboxDiv.appendChild(div);
            });
        });
    }

```


