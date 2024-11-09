const socket = new WebSocket(websocketUrl);
var span = document.getElementsByClassName("close")[0];
var feedback_button = document.getElementById("feedback-submit-button");

getAllConversations(conversations);
switchToConversation(conversations, 0);
socket.onclose = () => {window.location.reload();}
socket.onmessage = (event) => onMessage(event);

document.getElementById('user-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendUserQueryToBackend();
    }
  });

function onMessage(event){
    const data = JSON.parse(event.data)
    switch (data.type){
        case 'retrieve_ai_response':
            getAllMessages(data.message_history, streaming=true);
            let new_conversations = JSON.parse(data.conversations);
            getAllConversations(new_conversations);
            break;
        case 'get_all_conversations':
            getAllConversations(JSON.parse(data.conversations));
            switchToConversation(JSON.parse(data.conversations), -1);
            break;
        case 'get_questions_and_answers':
            getAllMessages(data.message_history);
            break;
        case 'update_thumbs_value':
            getAllMessages(data.message_history);
            switchToConversation(JSON.parse(data.conversations), data.conversation_id, use_index=false);
            break;
        case 'delete_conversation':
            getAllConversations(JSON.parse(data.conversations));
            getAllMessages(data.message_history);
            if(document.getElementsByClassName('chat-area')[0].id === data.delete_conversation_id){
                switchToConversation(JSON.parse(data.conversations), -1)
            }
            else{
                switchToConversation(JSON.parse(data.conversations), document.getElementsByClassName('chat-area')[0].id, use_index=false)
            }
            break;
    }
}

function submitFeedback(){
    user_feedback = document.getElementById("feedback-textarea").value;
    window.alert("Thank you for your feedback");
    let modal = document.getElementsByClassName("modal")[0];
    modal.style.display = "none";
    socket.send(JSON.stringify({type : 'submit_feedback', answer_id: modal.id.split("-").at(-1), feedback: user_feedback}));
}

function ChatBubble(user_query, speaker, chatBubbleId, thumbs_value) {
  const chatBox = document.getElementById("chat-box");
  const chatBubble = document.createElement("div");
  chatBubble.classList.add("chat-bubble", speaker);
  chatBubble.id = chatBubbleId;

  const message = document.createElement("p");
  message.textContent = user_query;
  chatBubble.appendChild(message);

  if(speaker === 'ai' && chatBubbleId.split("-").at(-1) != "undefined"){
    const clipboard = document.createElement("img")
    clipboard.src = "/static/images/copy.png";
    clipboard.className = "clipboard"
    clipboard.id = "clipboard-" + chatBubbleId;
    clipboard.title = 'Copy to clipboard';
    chatBubble.appendChild(clipboard);

    clipboard.addEventListener('click', function() {
    });

    const feedback = document.createElement("img")
    feedback.src = "/static/images/comment.png";
    feedback.className = "user-feedback";
    feedback.id = "user-feedback-" + chatBubbleId;
    feedback.title = 'Give feedback';
    chatBubble.appendChild(feedback);

    let modal = document.getElementsByClassName("modal")[0];

    feedback.addEventListener('click', function() {
        modal.style.display = "block";
        modal.id = "feedback-modal-" + chatBubbleId;
    });
    span.addEventListener('click', function() {
        modal.style.display = "none";
    });

    const thumbs_down_image = document.createElement("img")
    thumbs_down_image.src = "/static/images/dislike.png";
    thumbs_down_image.className = "thumbs-down";
    thumbs_down_image.id = "thumbs-down-" + chatBubbleId;
    thumbs_down_image.title = "I don't like this response";
    chatBubble.appendChild(thumbs_down_image);

    thumbs_down_image.addEventListener('click', function() {
        socket.send(JSON.stringify({type : 'update_thumbs_value', answer_id: chatBubbleId.split("-").at(-1), thumbs_value: -1, conversation_id: conversation_id, user_id : user_id}));
    });

    const thumbs_up_image = document.createElement("img")
    thumbs_up_image.src = "/static/images/like.png";
    thumbs_up_image.className = "thumbs-up";
    thumbs_up_image.id = "thumbs-up-" + chatBubbleId;
    thumbs_up_image.title = "I like this response";
    chatBubble.appendChild(thumbs_up_image);
    let conversation_id = document.getElementsByClassName('chat-area')[0].id

    thumbs_up_image.addEventListener('click', function() {
        socket.send(JSON.stringify({type : 'update_thumbs_value', answer_id: chatBubbleId.split("-").at(-1), thumbs_value: 1, conversation_id: conversation_id, user_id : user_id}));
    });

    if(thumbs_value === 1){
        thumbs_up_image.style.border = "2px solid rgb(26, 233, 26)";
    }
    else if(thumbs_value === -1){
        thumbs_down_image.style.border = "2px solid rgb(206, 9, 9)";
    }
    else{
        thumbs_up_image.style.border = "none";
        thumbs_down_image.style.border = "none";
    }
  }
  chatBox.appendChild(chatBubble);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function addUserChatBubble(userInput, chatBubbleId){
    ChatBubble(userInput, "user", "user-chat-bubble-" + chatBubbleId);
}

function addAIChatBubble(userInput, chatBubbleId, thumbs_value){
    ChatBubble(userInput, "ai", "ai-chat-bubble-" + chatBubbleId, thumbs_value);
}

function sendUserQueryToBackend(){
    const userInput = document.getElementById("user-input").value;
    if(userInput.trim() != ""){
        document.getElementById('user-input').value = "";
        const conversation_id = document.getElementsByClassName('chat-area')[0].id
        addUserChatBubble(userInput);
        socket.send(JSON.stringify({type : 'retrieve_ai_response', content : userInput, conversation_id : conversation_id, user_id : user_id}));
    }
}

function addConversation(){
    socket.send(JSON.stringify({type : 'add_conversation', user_id : user_id}));
}

function switchToConversation(conversations, conversation_index_or_id, use_index=true){
    let conversation_id;
    if(use_index){
        conversation_id = conversations.at(conversation_index_or_id)['id'];
    }
    else{
        conversation_id = conversation_index_or_id;
    }
    document.getElementById("chat-item-" + conversation_id.toString()).style.backgroundColor = "#7a7a79";
    const chatArea = document.getElementsByClassName('chat-area')[0];
    chatArea.id = conversation_id
    function sendMessage() {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'get_questions_and_answers',
                conversation_id: conversation_id,
                user_id: user_id
            }));
        } else {
            setTimeout(sendMessage, 100);
        }
    }
    sendMessage();
}


function getAllConversations(conversations) {
    const chatHistoryContainer = document.querySelector('.chat-history');
    chatHistoryContainer.innerHTML = '';
    const firstConversation = conversations[0];

    for (let conversation of conversations) {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        chatItem.id = 'chat-item-' + conversation['id'].toString();
        const conversationText = document.createTextNode("Conversation ID: " + conversation['id']);
        chatItem.appendChild(conversationText);

        const deleteIcon = document.createElement('img');
        deleteIcon.src = '/static/images/bin.png';
        deleteIcon.alt = 'Delete'; 
        deleteIcon.title = 'Delete conversation';
        deleteIcon.style.width = '20px'; 
        deleteIcon.style.height = '20px'; 
        deleteIcon.style.cursor = 'pointer';
        deleteIcon.style.float = "right";
        
        let isActionInProgress = false;

        deleteIcon.addEventListener('click', function() {
            if (!isActionInProgress) {
                isActionInProgress = true;
                console.log(`Deleting conversation with ID: ${chatItem.id}`);
                deleteConversation(chatItem.id, firstConversation['id']);
                setTimeout(() => isActionInProgress = false, 300); // Reset flag after a delay
            }
        });

        chatItem.addEventListener('click', function() {
            if (!isActionInProgress) {
                isActionInProgress = true;
                const chatItems = document.getElementsByClassName("chat-item");
                for (let item of chatItems) {
                    item.style.backgroundColor = "";
                }
                document.getElementById(chatItem.id).style.backgroundColor = "#7a7a79";
                const chatArea = document.getElementsByClassName('chat-area')[0];
                chatArea.id = conversation['id'];
                socket.send(JSON.stringify({type: 'get_questions_and_answers', conversation_id: conversation['id'], user_id: user_id}));
                setTimeout(() => isActionInProgress = false, 300); // Reset flag after a delay
            }
        });

        
        chatItem.appendChild(deleteIcon); 
        chatHistoryContainer.appendChild(chatItem);
    }
}

function deleteConversation(delete_conversation_id, first_conversation_id){
    socket.send(JSON.stringify(
        {
            type : 'delete_conversation', 
            delete_conversation_id : delete_conversation_id.split("-")[2], 
            first_conversation_id : first_conversation_id,
            user_id : user_id
        }
    ));
}
function streamMessage(message, containerId, delay = 30) {
    const container = document.getElementById(containerId);
    const paragraph = container.getElementsByTagName('p')[0];
    const userInput = document.getElementById('user-input');
    const userInputButton = document.getElementsByClassName("send-btn")[0];
    userInput.disabled = true;
    userInputButton.disabled = true;
    paragraph.innerHTML = "";
    let index = 0;

    function addNextCharacter() {
        if (index < message.length) {
            paragraph.innerHTML += message[index];
            index++;
            setTimeout(addNextCharacter, delay);
        } else {
            userInput.disabled = false;
            userInputButton.disabled = false;
        }
    }
    addNextCharacter();
}



function getAllMessages(message_history, streaming=false) {

    document.getElementById('chat-box').innerHTML = "";
    message_history = JSON.parse(message_history);
    addAIChatBubble("Hello! How can I help you today?");

    for (let message_index = 0; message_index < message_history.length; message_index++) {

        const message = message_history[message_index];

        if ("chat-bubble ai" in message && message_index == message_history.length - 1 && streaming === true){
            addAIChatBubble(message["chat-bubble ai"], message["id"], message["thumbs_value"]);
            streamMessage(message["chat-bubble ai"], "ai-chat-bubble-"+message["id"])
        }
        else if ("chat-bubble user" in message) {
            addUserChatBubble(message["chat-bubble user"], message["id"]);
        } else {
            addAIChatBubble(message["chat-bubble ai"], message["id"], message["thumbs_value"]);
        }
    }
}
