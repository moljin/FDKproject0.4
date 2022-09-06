"use strict"


const shopSubscribeCancelBtn = document.querySelector("#subscribe-cancel-btn");
shopSubscribeCancelBtn.addEventListener('click', function (e) {
    e.preventDefault();
    let request = $.ajax({
                url: shopCategorySubscribeCancelAjax,
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
                        // window.location.reload();
                        document.querySelector("#shop-subscribe-submit").style.display = "block";
                        document.querySelector("#subscribing-btn").style.display = "none";

                        let count = response.subscribe_count+2653;
                        let countSpan = document.querySelector(".shop-item.viewcount-subscribe-container > div > div.ml-15 > span");
                        countSpan.innerHTML = `구독: `+count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')+`명`;
                    }
                },
                error: function (err) {
                    console.log(err)
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });


}, false);