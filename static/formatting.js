function preventLetters(event) {
    return event.charCode >= 48 && event.charCode <= 57;
}

function unhideForm() {
    var x = document.getElementById("diff_category_div");
    console.log(x.style.display);
    if (x.style.display == "none") {
      x.style.display = "block";
    } else {
      x.style.display = "none";
    }
}