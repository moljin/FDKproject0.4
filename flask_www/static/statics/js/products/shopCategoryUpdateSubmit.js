"use strict"

const shopTitleCheckBtn = document.querySelector("#shoptitle-check-btn");
shopTitleCheckBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let shopcategory_title = document.querySelector("#shopcategory-title").value;
    console.log("shopcategory_title", shopcategory_title)
    let formData = new FormData();
    formData.append("title", shopcategory_title);
    let request = $.ajax({
                url: existingShopcategoryCheckAjax,
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
                        const flashAlert_div = document.querySelector(".shop-update-alert");
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


const shopUpdateSubmit = document.querySelector("#shop-update-submit");
shopUpdateSubmit.addEventListener('click', function (e) {
    // shopTitleCheckBtn.click();
    e.preventDefault();
    let shopcategory_title = document.querySelector("#shopcategory-title").value;
    let shopcategory_content = document.querySelector("#shopcategory-content").value;
    let meta_description = document.querySelector("#meta_description").value;
    let formData = new FormData();
    formData.append("title", shopcategory_title);
    formData.append("content", shopcategory_content);
    formData.append("meta_description", meta_description);

    let request = $.ajax({
                url: shopCategoryUpdateAjax,
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
                        const flashAlert_div = document.querySelector(".shop-update-alert");
                        if (response.flash_message === "동일한 상점타이틀이 존재합니다.") {
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
                                const shopTitleTag = document.querySelector("#shop-title");
                                const shopContent = document.querySelector("#shop-content");
                                const shopMetaDescription = document.querySelector("#shop-meta-description");

                                shopTitleTag.innerHTML = response.shopcategory_title;
                                shopContent.innerHTML = response.shopcategory_content;
                                shopMetaDescription.innerHTML = response.meta_description;
                                // document.querySelector("#shop-create-update-modal").style.display = "none";
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


const shopCategoryDeleteBtn = document.querySelector("#shop-delete-btn");
shopCategoryDeleteBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let request = $.ajax({
                url: shopCategoryDeleteAjax,
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
                        console.log('ShopCategory delete success');
                        // similar behavior as an HTTP redirect
                        // window.location.replace("http://stackoverflow.com");

                        // similar behavior as clicking on a link
                        // window.location.href = "http://stackoverflow.com";
                        window.location.href = response.profile_vendor_detail_url;
                    }
                },
                error: function (err) {
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });


}, false);