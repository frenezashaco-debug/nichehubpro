/* The existing form provider confirms acceptance; this is not a delivery receipt. */
(function () {
  'use strict';
  var form = document.getElementById('contact-form');
  if (!form) return;
  var button = document.getElementById('contact-btn');
  var success = document.getElementById('contact-success');
  var error = document.getElementById('contact-error');
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (button.disabled) return;
    success.hidden = true; error.hidden = true;
    button.disabled = true; button.textContent = 'Sending...';
    fetch(form.action, {method: 'POST', headers: {'Accept': 'application/json'}, body: new FormData(form)})
      .then(function (response) {
        if (!response.ok) throw Error('Form provider did not accept the message');
        success.hidden = false; form.reset();
      })
      .catch(function () { error.hidden = false; })
      .finally(function () { button.disabled = false; button.textContent = 'Send Message'; });
  });
}());
