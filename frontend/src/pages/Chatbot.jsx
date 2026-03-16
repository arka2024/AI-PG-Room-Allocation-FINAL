import Layout from "../components/Layout";
import { useState } from "react";

function Chatbot() {

const [messages,setMessages] = useState([
{
role:"bot",
text:`Hey there! 👋 I'm your CohabitAI assistant.

I can help you with:
• Profile optimization
• Search strategies
• Compare tool guidance
• Conflict resolution

What would you like help with?`
}
]);

const [input,setInput] = useState("");

function sendMessage(message){

if(!message.trim()) return;

const userMsg = {role:"user",text:message};

setMessages(prev=>[...prev,userMsg]);

setInput("");


setTimeout(()=>{

const botMsg={
role:"bot",
text:"This is a demo AI response. Your Flask/ML backend will reply here."
};

setMessages(prev=>[...prev,botMsg]);

},800);

}


return(

<Layout>

<section className="py-5" style={{marginTop:"70px"}}>

<div className="container">

<div className="row justify-content-center">

<div className="col-lg-8">

<div className="glass-card p-0 chatbot-container">

{/* HEADER */}

<div className="chat-header p-3 border-bottom border-secondary border-opacity-25">

<div className="d-flex align-items-center gap-3">

<div className="avatar-circle bg-accent">
🤖
</div>

<div>

<h5 className="fw-bold mb-0">
CohabitAI Assistant
</h5>

<small className="text-success">
● Online
</small>

</div>

</div>

</div>



{/* CHAT AREA */}

<div
className="chat-messages p-4"
style={{height:"400px",overflowY:"auto"}}
>

{messages.map((msg,i)=>(

<div
key={i}
className={`chat-bubble ${msg.role==="user"?"user":"bot"} mb-3`}
>

<div className="bubble-content">
{msg.text}
</div>

<small className="text-muted">
{msg.role==="user"?"You":"CohabitAI"}
</small>

</div>

))}

</div>



{/* QUICK BUTTONS */}

<div className="px-4 pb-2">

<div className="d-flex gap-2 flex-wrap">

<button
className="btn btn-outline-secondary btn-sm"
onClick={()=>sendMessage("How can I improve my profile?")}
>
📝 Profile Tips
</button>

<button
className="btn btn-outline-secondary btn-sm"
onClick={()=>sendMessage("How do I find better matches?")}
>
🔍 Search Tips
</button>

<button
className="btn btn-outline-secondary btn-sm"
onClick={()=>sendMessage("How does the compatibility algorithm work?")}
>
🧮 Algorithm
</button>

<button
className="btn btn-outline-secondary btn-sm"
onClick={()=>sendMessage("How does the compare tool work?")}
>
📊 Compare Tool
</button>

</div>

</div>



{/* INPUT */}

<div className="chat-input p-3 border-top border-secondary border-opacity-25">

<form
className="d-flex gap-2"
onSubmit={(e)=>{
e.preventDefault();
sendMessage(input);
}}
>

<input
type="text"
className="form-control glass-input"
placeholder="Ask something..."
value={input}
onChange={(e)=>setInput(e.target.value)}
/>

<button
type="submit"
className="btn btn-accent"
>
Send
</button>

</form>

</div>


</div>

</div>

</div>

</div>

</section>

</Layout>

)

}

export default Chatbot;