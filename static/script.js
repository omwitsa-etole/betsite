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