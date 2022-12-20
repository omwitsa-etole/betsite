$(document).ready(function(){
	fetch('/topnav')
	    .then(function(response) {
		return response.text()
		hideloader();
	    })
	    .then(function(html) {    
		document.getElementById("top-nav").innerHTML = html;
		
	    })
	    .catch(function(err) {  
		alert('Failed to fetch page: ', err);
		  
	    });
	
	if(location.search == "?login"){
		var y = document.getElementById("form-l");
		console.log(y)
		y.style.display = "block";	
		$("#form-l").load("/login");
	}else{
		var x = document.getElementById("form-l");
		if(x){
			x.style.display == "none";
		}
	}
})

function myFunction() {
	var x = document.getElementById("myDropdown");
	if(x.classList.contains("show")){
		x.classList.remove("show");
	}else{
  		document.getElementById("myDropdown").classList.toggle("show");
	}
}
function searchQuery(type){
	var input = document.getElementById("myInput").value;
	if(input.length > 0){
		input = input.replace(" ", "%20");
		location.href = "/search?"+type+"="+input;
	}
}
function searchBook(val){
	var input = document.getElementById("myInput").value;
	if(val != "" && val.length > 0){
		location.href = "/search?book="+val+"&&type="+input;		
	}
}
function searchBookmark(val){
	var input = document.getElementById("myInput").value;
	if(val != "" && val.length > 0){
		location.href = "/search?bookmark="+val+"&&matches="+input;		
	}
}
window.onclick = function(event) {
	if (!event.target.matches('.fa')) {
		var x = document.getElementsByClassName('dropdown-content-search');
		for(let i=0;i<x.length;i++){
			if(x[i].classList.contains("show")){
				x[i].classList.remove("show");
			}
		}
	}
}
function showBookmakers(){
	var x = document.getElementById("bookmarks");
	if(x.style.display == 'block'){
		x.style.display = 'none';
	}else{ x.style.display = 'block';}
}
function hideloader() {
    document.getElementById('loading').style.display = 'none';
}
function popup(text){
	if(text != "read"){
		var x = document.getElementById("snackbar");
		x.innerText = text;
		x.className = "show";
		setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
	}
	
}
dragElement(document.getElementById("mydiv"));

function dragElement(elmnt) {
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  if (document.getElementById(elmnt.id + "header")) {
    // if present, the header is where you move the DIV from:
    document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
  } else {
    // otherwise, move the DIV from anywhere inside the DIV:
    elmnt.onmousedown = dragMouseDown;
  }

  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves:
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    // set the element's new position:
    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    // stop moving when mouse button is released:
    document.onmouseup = null;
    document.onmousemove = null;
  }
}