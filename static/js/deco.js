
var mainNav = document.querySelector("#nav");
console.log(mainNav);

mainNav.addEventListener("mouseover", function() {
  mainNav.textContent = "mouse over";
  mainNav.style.color = 'red';
})
