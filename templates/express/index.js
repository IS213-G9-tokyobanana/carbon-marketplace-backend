// TODO
var express = require("express");
var app = express();
var port = 5000;
app.get("/", function (req, res) {
    res.send("Hello World!");
});
app.listen(port, function () {
    console.log("Example app listening on port ".concat(port));
});
