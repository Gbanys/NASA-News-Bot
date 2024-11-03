const socket = new WebSocket(websocketUrl);
getAllConversations(conversations);
switchToConversation(conversations, 0);
socket.onclose = () => {window.location.reload();}
socket.onmessage = (event) => onMessage(event);

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
        case 'delete_conversation':
            getAllConversations(JSON.parse(data.conversations));
            getAllMessages(data.message_history);
            if(document.getElementsByClassName('chat-area')[0].id === data.delete_conversation_id){
                switchToConversation(JSON.parse(data.conversations), -1)
            }
            break;
    }
}

function ChatBubble(user_query, speaker, chatBubbleId) {
  const chatBox = document.getElementById("chat-box");
  const chatBubble = document.createElement("div");
  chatBubble.classList.add("chat-bubble", speaker);
  chatBubble.id = chatBubbleId;

  const message = document.createElement("p");
  message.textContent = user_query;
  chatBubble.appendChild(message);
  chatBox.appendChild(chatBubble);

  chatBox.scrollTop = chatBox.scrollHeight;
}

function addUserChatBubble(userInput, chatBubbleId){
    ChatBubble(userInput, "user", "user-chat-bubble-" + chatBubbleId);
}

function addAIChatBubble(userInput, chatBubbleId){
    ChatBubble(userInput, "ai", "ai-chat-bubble-" + chatBubbleId);
}

function sendUserQueryToBackend(){
    const userInput = document.getElementById("user-input").value;
    const conversation_id = document.getElementsByClassName('chat-area')[0].id
    window.alert(conversation_id);
    addUserChatBubble(userInput);
    socket.send(JSON.stringify({type : 'retrieve_ai_response', content : userInput, conversation_id : conversation_id, user_id : user_id}));
}

function addConversation(){
    socket.send(JSON.stringify({type : 'add_conversation', user_id : user_id}));
}

function switchToConversation(conversations, conversation_index){
    let conversation_id = conversations.at(conversation_index)['id'];
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
        const conversationText = document.createTextNode(conversation['id']);
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
                const chatArea = document.getElementsByClassName('chat-area')[0];
                chatArea.id = conversation['id'];
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
    container.innerHTML = "";
    let index = 0;
    function addNextCharacter() {
        if (index < message.length) {
            container.innerHTML += message[index];
            index++;
            setTimeout(addNextCharacter, delay);
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
            addAIChatBubble(message["chat-bubble ai"], message["id"]);
            streamMessage(message["chat-bubble ai"], "ai-chat-bubble-"+message["id"])
        }
        else if ("chat-bubble user" in message) {
            addUserChatBubble(message["chat-bubble user"], message["id"]);
        } else {
            addAIChatBubble(message["chat-bubble ai"], message["id"]);
        }
    }
}
