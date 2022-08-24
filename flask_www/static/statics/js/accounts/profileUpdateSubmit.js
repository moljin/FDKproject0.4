"use strict"

const profileUpdateSubmitBtn = document.querySelector("#profile-update-submit");
profileUpdateSubmitBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let profile_nickname = document.querySelector("#profile-nickname").value;
    let profile_message = document.querySelector("#profile-message").value;
    let profile_image = document.querySelector("#profile_image").files[0];
    let formData = new FormData();
    formData.append("nickname", profile_nickname);
    formData.append("message", profile_message);
    formData.append("profile_image", profile_image);

    let request = $.ajax({
                url: profileUpdateAjax,
                type: 'POST',
                data: formData,
                headers: {"X-CSRFToken": CSRF_TOKEN,},
                dataType: 'json',
                async: false,
                cache: false,
                contentType: false,
                processData: false,

                success: function (response) {
                    if (response.error) {
                        alert("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + response.error);
                    } else {
                        console.log('nickname ==> ', response.profile_nickname);
                        console.log('message ==> ', response.profile_message);
                        console.log('image_path ==> ', response.profile_image_path);
                        // window.location.reload()
                        const profileNicknameTag = document.querySelector("#nickname");
                        const profileMessageTag = document.querySelector("#message");
                        const profileImagePathTag = document.querySelector("#image_path");

                        profileNicknameTag.innerHTML = response.profile_nickname;
                        profileMessageTag.innerHTML = response.profile_message;
                        profileImagePathTag.setAttribute("src", "/" + response.profile_image_path);

                    }
                },
                error: function (err) {
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });


}, false);


const profileDeleteBtn = document.querySelector("#profile-delete-btn");
profileDeleteBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let request = $.ajax({
                url: profileDeleteAjax,
                type: 'POST',
                data: {},
                headers: {"X-CSRFToken": CSRF_TOKEN,},
                dataType: 'json',
                async: false,
                cache: false,
                contentType: false,
                processData: false,

                success: function (response) {
                    if (response.error) {
                        alert("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + response.error);
                    } else {
                        console.log('Profile delete success');
                        // similar behavior as an HTTP redirect
                        // window.location.replace("http://stackoverflow.com");

                        // similar behavior as clicking on a link
                        // window.location.href = "http://stackoverflow.com";
                        window.location.href = response.account_dashboard_url;
                    }
                },
                error: function (err) {
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });


}, false);