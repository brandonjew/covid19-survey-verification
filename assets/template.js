var date = new Date();
var receipt = document.getElementById("receipt").textContent;
var receiptDate = new Date(document.getElementById("keydate").textContent);
var qrcode = new QRCode("qrcode", {
    width: 300,
    height: 300,
});
qrcode.makeCode(receipt);

var age = date - receiptDate;
var squareColor = "grey-square";

if (age < 0) {
  // Comes from the future :O
  squareColor = "grey-square";
} else if (age < 8.64e7) {
  // Less than a day old
  squareColor = "blue-square";
} else if (age < 6.048e8) {
  // Less than a week old
  squareColor = "yellow-square";
} else {
  // Older than a week
  squareColor = "red-square";
}

document.getElementById("square").className = squareColor; 

var html = [
  `<center>`,
    `<br>`,
    `<button onclick="changeTimeStyle()" class="rbutton">Toggle 12 or 24 hour</button>`,
  `</center>`,
  '<div class="footer">',
    '<h1>About</h1>',
    '<p>',
    'This is a non-identifiable completion receipt for the STOPCOVID symptom survey.',
    'It simply provides evidence of a survey completed at a given time.',
    '</p>',
    '<p>Color coding indicates age of receipt at time of page loading.</p>',
    '<div class="color-box" style="background-color: #88CCEE;">Today</div>',
    '<div class="color-box" style="background-color: #DDCC77;">This Week</div>',
    '<div class="color-box" style="background-color: #CC6677;">Older</div>',
  '</div>'
].join('');

var div = document.createElement('div');
div.setAttribute('class', 'post block bc2');
div.innerHTML = html;
document.getElementById('jsfooter').appendChild(div);

var options = {
  year: 'numeric',
  month: 'long',
  day: '2-digit',
  hour: 'numeric',
  minute: 'numeric',
  hour12: true,
  timeZoneName: 'short',
};

document.getElementById("keydate").textContent = new Intl.DateTimeFormat('default', options).format(receiptDate);
document.getElementById("now").textContent = new Intl.DateTimeFormat('default', options).format(date);

function changeTimeStyle() {
  options.hour12 = !(options.hour12)
  document.getElementById("keydate").textContent = new Intl.DateTimeFormat('default', options).format(receiptDate);
  document.getElementById("now").textContent = new Intl.DateTimeFormat('default', options).format(date);
}

