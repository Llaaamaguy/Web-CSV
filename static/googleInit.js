function init() {
    gapi.load('client', () => {
        console.log("loaded client");

        gapi.client.init({
            clientId: "592625169683-8orjkfnnnp3ceslq9d5oc2bvq8b4nsdg.apps.googleusercontent.com",
            scope: "https://www.googleapis.com/auth/userinfo.email"
        });
    })
}

init();
function getUserData() {
    var auth2 = gapi.auth2.getAuthInstance();
    if (auth2.isSignedIn.get()) {
        var profile = auth2.currentUser.get().getBasicProfile();
        document.getElementById('username').innerHTML = profile.getName();
        document.getElementById('useremail').innerHTML = profile.getEmail();
        var userImage = profile.getImageUrl();
    }
}

getUserData();