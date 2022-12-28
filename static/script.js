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
function sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
   }

var span_time = document.getElementById('time-now');
setInterval(time, 1000);


function time() {
	  if(location.search.includes("time=")){
		var n = document.getElementById("by-time");
		n.setAttribute("style", "background: black;color: yellow;")
	  }
	  if(location.search.includes("filter=")){
		let x = location.search;
		if(x.includes("&&")){
			let r = x.split("&&");
			x = r[1];
			x = x.replace("filter=", "");
		}else{
			x = x.replace("?filter=", "");
		}
		var z = document.getElementById("book-filter");
		var m = document.getElementById("bookm-makers");
		z.innerText = x;
		m.setAttribute("style", "background: black;")
	  }
	  var span_time = document.getElementById('time-now');
	  var d = new Date();
	  var s = d.getSeconds();
	  var m = d.getMinutes();
	  var h = d.getHours();
	  span_time.textContent = 
	    ("0" + h).substr(-2) + ":" + ("0" + m).substr(-2) + ":" + ("0" + s).substr(-2);
	}


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

function makeActive(el, id){	
	if(id != "null"){
		var x = document.getElementById(id)
		if(x.style.display == 'block'){
			x.style.display='none';
		}else{ x.style.display = 'block';}
	}
	if(el.classList.contains('active')){
		el.classList.remove('active');
	}else{
		el.classList.add('active')
	}
}
function filterCountries(){
	 var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("search-books");
  filter = input.value.toUpperCase();
  table = document.getElementById("book-list");
  tr = table.getElementsByTagName("button");
  let x = tr.length;
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("span")[0];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
	x = x -1;	
      }
    }
  }
}

function filterB(val){
	x = location.search;
	y = location.href;
	if(x.includes("&&")){
		let r = x.split("&&");
		console.log(r);
		x = r[0];
		location.search = x+"&&filter="+val;	
	}else if(x.includes("?league")){
		location.search = x+"&&filter="+val;		
	}else{
		location.search = "?filter="+val
	}
}