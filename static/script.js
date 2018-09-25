var timeoutID;
var timeout = 1000;

function setup() {
	var sendButton = document.getElementById("sendButton");
	var message = document.getElementById("message");
	sendButton.addEventListener("click", makePost, true);
	message.addEventListener("keydown", function(e) {
		if (e.keyCode === 13) {
			sendButton.click();
		}
	}, true);

	timeoutID = window.setTimeout(poller, timeout);
}

function makePost() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	var message = document.getElementById("message").value
	httpRequest.onreadystatechange = function() { handlePost(httpRequest) };
	
	httpRequest.open("POST", "/newMessage");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	var data = "message=" + JSON.stringify(message);
	
	httpRequest.send(data);
}

function handlePost(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			clearInput();
		} else {
			alert("There was a problem with the post request.");
		}
	}
}

function poller() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	httpRequest.onreadystatechange = function() { handlePoll(httpRequest) };
	httpRequest.open("GET", "/messages");
	httpRequest.send();
}

function handlePoll(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			var messages = JSON.parse(httpRequest.responseText);
			for (var i = 0; i < messages.length; i++) {
				addMessage(messages[i]);
			}
			
			timeoutID = window.setTimeout(poller, timeout);
			
		} else {
			alert("There was a problem with the poll request.  you'll need to refresh the page to recieve updates again!");
		}
	}
}

function clearInput() {
	document.getElementById("message").value = "";
}

function addMessage(message) {
	var ul = document.getElementById("messages");
	var li = document.createElement("li");
	var b = document.createElement("b");
	b.appendChild(document.createTextNode(message[0]))
	li.appendChild(b);
	li.appendChild(document.createTextNode(message[1]))
	ul.appendChild(li);
}

window.addEventListener("load", setup, true);
