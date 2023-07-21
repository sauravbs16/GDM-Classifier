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
  let age = document.getElementById('age').value;
  let bmi = document.getElementById('bmi').value;
  let height = document.getElementById('height').value;
  let ethnicity = document.getElementById('ethnicity').value;
  let obesity = document.getElementById('obese').value === 'Yes';
  let isFirstPregnancy = document.getElementById('first-pregnancy').value === 'Yes';

  let postObj = {
    user_id: username,
    email:email,
    password: password,
    age: age,
    bmi: bmi,
    height: height,
    obesity: obesity,
    ethnicity: ethnicity,
    is_first_pregnancy: isFirstPregnancy
  }

  let post = JSON.stringify(postObj)
  const url = "/signup"
  let xhr = new XMLHttpRequest()
  
  xhr.open('POST', url, true)
  xhr.setRequestHeader('Content-type', 'application/json; charset=UTF-8')
  xhr.send(post);

  xhr.onload = function () {
    if (this.readyState == 4 && this.status == 200) {
      if (xhr.responseText == "True"){
        window.location.href = "dashboard";
      } else {
        document.getElementById("sign-info").innerHTML = xhr.responseText;
      }
    };
  }

});

document.getElementById('signin-btn').addEventListener('click', (event) => {
  event.preventDefault();
  // Retrieve form values
  let signinUsername = document.getElementById('signin-username').value;
  let signinPassword = document.getElementById('signin-password').value;

  let postObj = {
    user_id: signinUsername,
    password: signinPassword
  }

  let post = JSON.stringify(postObj)
  const url = "/login"
  let xhr = new XMLHttpRequest()
  
  xhr.open('POST', url, true)
  xhr.setRequestHeader('Content-type', 'application/json; charset=UTF-8')
  xhr.send(post);

  xhr.onload = function () {
    if (this.readyState == 4 && this.status == 200) {
      if (xhr.responseText == "True"){
        window.location.href = "dashboard";
      } else {
        document.getElementById("sign-info").innerHTML = "Incorrect credentials";
      }
    };
  }

  // Transition to the second page or perform any desired action
  //container.classList.remove('sign-in');
  //container.classList.add('sign-up');
});

setTimeout(() => {
  container.classList.add('sign-in');
}, 200);
