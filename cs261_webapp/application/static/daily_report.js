
function generateModal(){
  // Display the modal
  document.querySelector('.generate_modal').style.display = "block";
  // Block the other content
  document.querySelector('.main_content').style.display = "none";
}

function searchModal(){
  // Displays the modal
  document.querySelector('.search_modal').style.display = "block";
  // Block the other content
  document.querySelector('.main_content').style.display = "none";
}

function closeModal(){
  // Closes the modal
  document.querySelector('.generate_modal').style.display = "none";
  document.querySelector('.search_modal').style.display = "none";
  // Displays main content
  document.querySelector('.main_content').style.display = "block";
}
