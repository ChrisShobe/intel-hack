import React, { useState } from "react";
function Home() {
const [message, setMessage] = useState("");
function sendMessage () {
const apiURL = "http://localhost:3000/api/message?message=" + message;
fetch(apiURL, {
method: "GET",
headers: {
"Content-Type": "application/json",
},
})
.then((response) => {
if (!response.ok) {
throw new Error("Network response was not ok");
}
return response.json();
})
.then((data) => {
alert("Response: " + JSON.stringify(data));
alert("Response message: " + data.message);
})
.catch((error) => {
alert("Error: " + error.message);
});
};
return (
<div className="flex flex-col items-center justify-center min-h-screen">
<h1>Send a message</h1>
<input
type="text"
value={message}
onChange={(e) => setMessage(e.target.value)}
placeholder="Type your message here"
/>
<button onClick={sendMessage}>Send</button>
</div>
);
}
export default Home;