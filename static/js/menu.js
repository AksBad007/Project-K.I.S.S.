const users = $(".users");
const submissions = $(".submissions");
const summary = $(".summary");
const heading = $(".offer");

$("#users").click(function() {
    users.css({'opacity': 1, "z-index": 1});
    submissions.css({'opacity': 0, "z-index": 0});
    summary.css({'opacity': 0, "z-index": 0});
    heading.text("User Info");
});

$("#submissions").click(function() {
    users.css({'opacity': 0, "z-index": 0});
    submissions.css({'opacity': 1, "z-index": 1});
    summary.css({'opacity': 0, "z-index": 0});
    heading.text("Submissions");
});

$("#summary").click(function() {
    users.css({'opacity': 0, "z-index": 0});
    submissions.css({'opacity': 0, "z-index": 0});
    summary.css({'opacity': 1, "z-index": 1});
    heading.text("So Far We Have...");
});

$("#submit").click(function() {
    $("#success").css({'opacity':1, "z-index": 1});
    $(".form-signin").css({'opacity':0, "z-index": 0});
});