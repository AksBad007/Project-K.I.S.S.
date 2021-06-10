let html = document.querySelector("#HTML-code");
let css = document.querySelector("#CSS-code");
let js = document.querySelector("#JS-code");
let output = document.querySelector("#output");
let bar = document.querySelector("#bar");

function run(){
    let htmlCode = html.value;
    let cssCode = "<style>" + css.value + "</style>";
    let jsCode = js.value;
    
    output.contentDocument.body.innerHTML = htmlCode+cssCode;
    output.contentWindow.eval(jsCode);
}

html.addEventListener("keyup",run);
css.addEventListener("keyup",run);
js.addEventListener("keyup",run);