let container = document.getElementById('container');

toggle = () => {
  container.classList.toggle('sign-in');
  container.classList.toggle('sign-up');
};

document.getElementById('signup-btn').addEventListener('click', (event) => {
  event.preventDefault();
  // Retrieve form values
  let username = document.getElementById('username').value;
  let email = document.getElementById('email').value;
  let password = document.getElementById('password').value;
  let confirmPassword = document.getElementById('confirm-password').value;
  let age = document.getElementById('age').value;
  let bmi = document.getElementById('bmi').value;
  let ethnicity = document.getElementById('ethnicity').value;
  let isFirstPregnancy = document.getElementById('first-pregnancy').value === 'Yes';
  let hasPreviousGDM = document.getElementById('previous-gdm').value === 'Yes';

  // Perform form validation and submission logic here
  // ...

  // Transition to the second page or perform any desired action
  container.classList.remove('sign-up');
  container.classList.add('sign-in');
});

document.getElementById('signin-btn').addEventListener('click', (event) => {
  event.preventDefault();
  // Retrieve form values
  let signinUsername = document.getElementById('signin-username').value;
  let signinPassword = document.getElementById('signin-password').value;

  // Perform sign-in logic here
  // ...

  // Transition to the second page or perform any desired action
  container.classList.remove('sign-in');
  container.classList.add('sign-up');
});

setTimeout(() => {
  container.classList.add('sign-in');
}, 200);
