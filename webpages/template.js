var s = document.getElementsByTagName('p');
var date = new Date();
var receipt = document.getElementById("receipt").textContent;
var receiptDate = new Date(document.getElementById("keydate").textContent);
var qrcode = new QRCode("qrcode", {
    width: 300,
    height: 300,
});

qrcode.makeCode(receipt);

console.log(receiptDate);
console.log(date);
