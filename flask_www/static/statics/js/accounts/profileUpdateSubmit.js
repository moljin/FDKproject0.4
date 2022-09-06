"use strict"

const nicknameCheckBtn = document.querySelector("#nickname-check-btn");
nicknameCheckBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let profile_nickname = document.querySelector("#profile-nickname").value;
    console.log("profile_nickname", profile_nickname)
    let formData = new FormData();
    formData.append("nickname", profile_nickname);
    let request = $.ajax({
                url: existingProfileCheckAjax,
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
                        const flashAlert_div = document.querySelector(".profile-update-alert");
                        if (response.flash_message) {
                            flashAlert_div.innerHTML = `<div class="flashes" uk-alert id="subscribe-alert">
                                                        <div class="alert alert-danger" role="alert">`+response.flash_message+`</div>
                                                        <button class="uk-alert-close mt-5" type="button" uk-close></button></div>`
                            // window.location.reload();
                        } else {
                            flashAlert_div.innerHTML = `<div class="flashes" uk-alert id="subscribe-alert">
                                                        <div class="alert alert-danger" role="alert">사용 가능합니다.</div>
                                                        <button class="uk-alert-close mt-5" type="button" uk-close></button></div>`
                        }
                    }
                },
                error: function (err) {
                    console.log(err)
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });
}, false);

const profileUpdateSubmitBtn = document.querySelector("#profile-update-submit");
profileUpdateSubmitBtn.addEventListener('click', function (e) {
    // nicknameCheckBtn.click();
    e.preventDefault();
    let profile_nickname = document.querySelector("#profile-nickname").value;
    let profile_message = document.querySelector("#profile-message").value;
    // let profile_image = document.querySelector("#profile_image").files[0];
    let formData = new FormData();
    formData.append("nickname", profile_nickname);
    formData.append("message", profile_message);
    // formData.append("profile_image", profile_image);

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
                        const flashAlert_div = document.querySelector(".profile-update-alert");
                        if (response.flash_message) {
                            flashAlert_div.innerHTML = `<div class="flashes" uk-alert id="subscribe-alert">
                                                        <div class="alert alert-danger" role="alert">`+response.flash_message+`</div>
                                                        <button class="uk-alert-close mt-5" type="button" uk-close></button></div>`
                        } else {
                            if (response.checked_message) {
                                flashAlert_div.innerHTML = `<div class="flashes" uk-alert id="subscribe-alert">
                                                        <div class="alert alert-danger" role="alert">`+response.checked_message+`</div>
                                                        <button class="uk-alert-close mt-5" type="button" uk-close></button></div>`
                            }
                            else {
                                const profileNicknameTag = document.querySelector("#nickname");
                                const profileMessageTag = document.querySelector("#message");
                                // const profileImagePathTag = document.querySelector("#image_path");
                                // const globalProfileImgTag = document.querySelector("#global-profile-img");

                                profileNicknameTag.innerHTML = response.profile_nickname;
                                profileMessageTag.innerHTML = response.profile_message;
                                // profileImagePathTag.setAttribute("src", "/" + response.profile_image_path);
                                // globalProfileImgTag.setAttribute("src", "/" + response.profile_image_path);
                                // document.querySelector("#basic-profile-update").style.display = "none";
                            }

                        }
                    }
                },
                error: function (err) {
                    console.log(err)
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


const profileImgSubmitBtn = document.querySelector("#profile-img-submit-btn");
profileImgSubmitBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let profile_image = document.querySelector("#profile_image").files[0];
    let deleteModalBtn = document.querySelector(".profile-img-modal-delete-btn");
    let formData = new FormData();
    formData.append("profile_image", profile_image);
    let request = $.ajax({
                url: profileImageSaveAjax,
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
                        const profileImgPathTag = document.querySelector("#image_path");
                        let image_path = response.image_path;
                        profileImgPathTag.setAttribute("src", "/" + image_path);
                        profileImgPathTag.classList.remove('inactive');
                        profileImgPathTag.style.display = "block";
                        deleteModalBtn.setAttribute("href", "#profile_img_delete_modal-container");
                        deleteModalBtn.style.display = "block";
                        document.querySelector("#profile_img_upload_modal-container").style.display = "none";
                    }
                },
                error: function (err) {
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });
}, false);


const profileImgDeleteBtn = document.querySelector("#profile-img-delete-btn");
profileImgDeleteBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let deleteModalBtn = document.querySelector(".profile-img-modal-delete-btn");
    let request = $.ajax({
                url: profileImageDeleteAjax,
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
                        const profileImgPathTag = document.querySelector("#image_path");
                        let image_path = response.image_path;
                        profileImgPathTag.setAttribute("src", "/" + image_path);
                        deleteModalBtn.classList.add('inactive');
                        deleteModalBtn.style.display = "none";
                        deleteModalBtn.removeAttribute("href");
                        console.log('success delete');

                    }
                },
                error: function (err) {
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });

}, false);