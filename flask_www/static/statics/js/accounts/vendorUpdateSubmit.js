"use strict"

const vendorUpdateSubmitBtn = document.querySelector("#vendor-update-submit");
vendorUpdateSubmitBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let corp_email = document.querySelector("#corp_email").value;
    let corp_number = document.querySelector("#corp_number").value;
    let corp_image = document.querySelector("#corp_image").files[0];
    let corp_address = document.querySelector("#corp_address").value;
    let main_phonenumber = document.querySelector("#main_phonenumber").value;
    let main_cellphone = document.querySelector("#main_cellphone").value;
    let profile_level = document.querySelector("#profile_level").value;
    let formData = new FormData();
    formData.append("corp_email", corp_email);
    formData.append("corp_number", corp_number);
    formData.append("corp_image", corp_image);
    formData.append("corp_address", corp_address);
    formData.append("main_phonenumber", main_phonenumber);
    formData.append("main_cellphone", main_cellphone);
    formData.append("level", profile_level);

    let request = $.ajax({
                url: vendorUpdateAjax,
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
                        console.log('corp_email ==> ', response.corp_email);
                        console.log('corp_number ==> ', response.corp_number);
                        console.log('corp_image_path ==> ', response.corp_image_path);
                        console.log('corp_address ==> ', response.corp_address);
                        console.log('main_phonenumber ==> ', response.main_phonenumber);
                        console.log('main_cellphone ==> ', response.main_cellphone);
                        // window.location.reload()
                        const corpEmailTag = document.querySelector("#profile_corp_email");
                        const corpNumberTag = document.querySelector("#profile_corp_number");
                        const corpImagePathTag = document.querySelector("#profile_corp_image_path");
                        const corpAddressTag = document.querySelector("#profile_corp_address");
                        const mainPhonenumberTag = document.querySelector("#profile_main_phonenumber");
                        const mainCellphoneTag = document.querySelector("#profile_main_cellphone");
                        const levelTag = document.querySelector("#level");

                        corpEmailTag.innerHTML = response.corp_email;
                        corpNumberTag.innerHTML = response.corp_number;
                        corpImagePathTag.setAttribute("src", "/" + response.corp_image_path);
                        corpAddressTag.innerHTML = response.corp_address;
                        mainPhonenumberTag.innerHTML = response.main_phonenumber;
                        mainCellphoneTag.innerHTML = response.main_cellphone;
                        levelTag.innerHTML = response.profile_level;
                    }
                },
                error: function (err) {
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });


}, false);


const vendorDeleteBtn = document.querySelector("#vendor-delete-btn");
vendorDeleteBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let request = $.ajax({
                url: vendorDeleteAjax,
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
                        console.log('vendor delete success');
                        window.location.reload()
                    }
                },
                error: function (err) {
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });


}, false);