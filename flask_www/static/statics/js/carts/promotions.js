"use strict"
/*jshint esversion: 6 */
promotionsInit();
function promotionsInit(){
    const couponApplyBtn = document.querySelector("#coupon-apply");
    couponApplyBtn.addEventListener("click", function (e){
        console.log("click")
    }, false);
}