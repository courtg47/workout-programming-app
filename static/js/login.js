/* JavaScript file for the login.html page. This is for Google Sign In. */

function signInCallback(authResult) {
  if (authResult['code']) {
    //Hide the sign-in button once authorized
    $("#signinButton").attr('style', 'display: none');

    /*Send one time use code to server and write a 'Login Successful'
    message to the page and redirect back to the homepage */
    $.ajax({
      type: 'POST',
      url: '/gconnect?state={{STATE}}',
      processData: false,
      contentType: 'application/octet-stream; charset=utf-8',
      data: authResult['code'],
      success: function(result) {
        if (result) {
          $('#result').html('Your Login is Successful!</br>' + result + '</br>Redirecting...');
          $(".disclaimer").attr('style', 'display: none');
          setTimeout(function() {
            window.location.href = "/exercises";
          }, 4000);
        } else if (authResult['error']) {
          console.log("We're sorry, an error has occurred: " + authResult['error']);
          $('#result').html("We're sorry, we cannot log you in right now due to an error.");
      } else {
        $('#result').html("Failed to make a server-side call. Check your configuration and console.");
      }
    }

    });
    }
  }
