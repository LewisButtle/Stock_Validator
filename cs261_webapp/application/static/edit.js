
var date = false;
var trade_id = false;
var product = false;
var buying_party = false;
var selling_party = false;
var underlying_currency = false;
var quantity = false;
var maturity_date = false;

// This function is run on the page load, and if submit was clicked and a form
// did not validate, then it would have been hidden. This loads all open fields
// window.onload=function(){
//   document.querySelector('#form').addEventListener("load",openField());
// }
//
// function openField(){
//   if(date==true){
//     alert("date is true");
//     document.querySelector('#date').style.display="block";
//   }else{
//     alert("date is false");
//   }
// }


function date_option_clicked(){
  if (date==false){
    document.querySelector('#date').style.display="block";
    date = true;
  }else{
    document.querySelector('#date').style.display="none";
    date = false;
  }
}

function trade_id_option_clicked(){
  if (trade_id==false){
    document.querySelector('#trade_id').style.display="block";
    trade_id = true;
  }else{
    document.querySelector('#trade_id').style.display="none";
    trade_id = false;
  }
  document.getElementById("date_option").checked = false;
}

function product_option_clicked(){
  if (product==false){
    document.querySelector('#product').style.display="block";
    product = true;
  }else{
    document.querySelector('#product').style.display="none";
    product= false;
  }
}

function buying_party_option_clicked(){
  if (buying_party==false){
    document.querySelector('#buying_party').style.display="block";
    buying_party = true;
  }else{
    document.querySelector('#buying_party').style.display="none";
    buying_party= false;
  }
}

function selling_party_option_clicked(){
  if (selling_party==false){
    document.querySelector('#selling_party').style.display="block";
    selling_party = true;
  }else{
    document.querySelector('#selling_party').style.display="none";
    selling_party= false;
  }
}

function underlying_currency_option_clicked(){
  if (underlying_currency==false){
    document.querySelector('#underlying_currency').style.display="block";
    underlying_currency = true;
  }else{
    document.querySelector('#underlying_currency').style.display="none";
    underlying_currency= false;
  }
}

function quantity_option_clicked(){
  if (quantity==false){
    document.querySelector('#quantity').style.display="block";
    quantity = true;
  }else{
    document.querySelector('#quantity').style.display="none";
    quantity= false;
  }
}

function maturity_date_option_clicked(){
  if (maturity_date==false){
    document.querySelector('#maturity_date').style.display="block";
    maturity_date = true;
  }else{
    document.querySelector('#maturity_date').style.display="none";
    maturity_date= false;
  }
}

// Sets all variables to false when the submit button is clicked
// Prevents checkboxes being initially set when the page reloads
// function clear(){
//   alert("hello");
//   date=false;
//   trade_id=false;
//   product=false;
//   buying_party=false;
//   selling_party=false;
//   underlying_currency = false;
//   quantity = false;
//   maturity_date = false;
//   document.getElementById("date_option").checked = false;
//
// }
