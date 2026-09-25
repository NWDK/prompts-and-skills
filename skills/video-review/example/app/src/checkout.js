// Checkout step. Validates the postcode, then moves to the next step.

var STEPS = ['checkout', 'review', 'confirmation'];

function nextStep(current) {
  var next = STEPS[STEPS.indexOf(current) + 1];
  if (next === 'review' && !flag('reviewStep')) {
    next = 'confirmation';
  }
  return next + '.html';
}

function showBanner(message) {
  var banner = document.getElementById('banner');
  banner.textContent = message;
  banner.hidden = false;
}

document.getElementById('checkout-form').addEventListener('submit', function (event) {
  event.preventDefault();
  var postcode = document.getElementById('postcode').value;

  if (!postcode.trim()) {
    showBanner('Postcode is required');
    return;
  }

  window.location.href = nextStep('checkout');
});
