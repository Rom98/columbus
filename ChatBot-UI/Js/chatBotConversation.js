// Selecting element to view chat
var chatBotSession              = document.querySelector( ".chatBot .chatBody .chatSession" )

// Selecting trigger elements of conversation
var chatBotSendButton           = document.querySelector( ".chatBot .chatForm #sendButton" )
var chatBotTextArea             = document.querySelector( ".chatBot .chatForm #chatTextBox" )

// Default values for replies
var chatBotInitiateMessage      = "Hello! I am Columbus."
var chatBotBlankMessageReply    = "Type something!"
var chatBotReply                = "{{ reply }}"
var response                    = ""
var url                 = ""
var options             = ""
// Collecting user input
var inputMessage                = ""

// This helps generate text containers in the chat
var typeOfContainer             = ""

async function getapi(url,options) {
    
    // Storing response
    const response = await fetch(url,options);
    
    // Storing data in form of JSON
    var data = await response.json();
    console.log(data[0].text);
    return data[0].text
}
// Function to start ChatBot
chatBotSendButton.addEventListener("click", (event)=> {
    // Since the button is a submit button, the form gets submittd and the complete webpage reloads. This prevents the page from reloading. We would submit the message later manually
    event.preventDefault()
    if( validateMessage() ){
        inputMessage    = chatBotTextArea.value
        var payload = JSON.stringify({"sender":"test_user","message":inputMessage});
        url = "http://127.0.0.1:5005/webhooks/rest/webhook";
        options = {method:"post",body:payload,headers:{"contentType":"application/json"}};
        typeOfContainer = "message";
        createContainer( typeOfContainer )
        setTimeout(function(){
            typeOfContainer = "reply"
            createContainer( typeOfContainer )
        }, 750);
        //response = UrlFetchApp.fetch(url, options);
        //  console.log(response)
    }
    else{        
        typeOfContainer = "error";
        createContainer( typeOfContainer )
    }
    chatBotTextArea.value = ""
    chatBotTextArea.focus()
})

async function createContainer( typeOfContainer ) {
    var containerID = ""
    var textClass   = ""
    switch( typeOfContainer ) {
        case "message"      :
            // This would create a message container for user's message
            containerID = "messageContainer"
            textClass   = "message"
            break;
        case "reply"        :
            containerID = "replyContainer"
            textClass   = "reply"
            break;
        case "initialize"   :
        case "error"        :
            // This would create a reply container for bot's reply
            containerID = "replyContainer"
            textClass   = "reply"
            break;
        default :
            alert("Error! Please reload the webiste.")
    }

    // Creating container
    var newContainer = document.createElement( "div" )
    newContainer.setAttribute( "class" , "container" )
    if( containerID == "messageContainer" )
        newContainer.setAttribute( "id" , "messageContainer" )
    if( containerID == "replyContainer" )
        newContainer.setAttribute( "id" , "replyContainer" )
    chatBotSession.appendChild( newContainer )

    switch( textClass ) {
        case "message"  :
            var allMessageContainers    = document.querySelectorAll("#messageContainer")
            var lastMessageContainer    = allMessageContainers[ allMessageContainers.length - 1 ]
            var newMessage              = document.createElement( "p" )
            newMessage.setAttribute( "class" , "message animateChat" )
            newMessage.innerHTML        = inputMessage
            lastMessageContainer.appendChild( newMessage )
            lastMessageContainer.scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"})
            break
        case "reply"    :
            var allReplyContainers      = document.querySelectorAll( "#replyContainer" )    
            var lastReplyContainer      = allReplyContainers[ allReplyContainers.length - 1 ]
            var newReply                = document.createElement( "p" )
            newReply.setAttribute( "class" , "reply animateChat accentColor" )
            switch( typeOfContainer ){
                case "reply"        :
                    chatBotReply = await getapi(url,options)
                    newReply.innerHTML  = chatBotReply
                    break
                case "initialize"   :
                    newReply.innerHTML  = chatBotInitiateMessage
                    break
                case "error"        :
                    newReply.innerHTML  = chatBotBlankMessageReply
                    break
                default             :
                    newReply.innerHTML  = "Sorry! I could not understannd."
            }
            setTimeout(function (){
                lastReplyContainer.appendChild( newReply )
                lastReplyContainer.scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"})
            }, 10)            
            break
        default         :
            console.log("Error in conversation")
    }
}

function initiateConversation() {
    chatBotSession.innerHTML = ""
    typeOfContainer = "initialize"
    createContainer( typeOfContainer )
}