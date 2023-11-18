// Show/hide password onClick of button using Javascript only

// https://stackoverflow.com/questions/31224651/show-hide-password-onclick-of-button-using-javascript-only

window.onload = function () {
    function show() {
        const p = document.getElementById('password');
        p.setAttribute('type', 'text');
    }

    function hide() {
        const p = document.getElementById('password');
        p.setAttribute('type', 'password');
    }

    let pwShown = 0;
    let eye = $('#eye')

    document.getElementById("eye").addEventListener("click", function () {
        if (pwShown === 0) {
            pwShown = 1;
            show();
            eye.addClass("fa-eye");
            eye.removeClass("fa-eye-slash");
        } else {
            pwShown = 0;
            hide();
            eye.removeClass("fa-eye");
            eye.addClass("fa-eye-slash");
        }
    }, false);

}
