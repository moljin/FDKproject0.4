"use strict"
/*jshint esversion: 6 */
cartInit();
function cartInit () {
    // product count change
    const productContainerAll = document.querySelectorAll(".product.p-container");
    productContainerAll.forEach(function (productContainer){
        const productId = productContainer.getAttribute("data-product-id");
        const pdPlusBtn = document.querySelector('[id="pd-plus-' + `${productId}` + '"]');
        const pdMinusBtn = document.querySelector('[id="pd-minus-' + `${productId}` + '"]');
        const pd_type = "product";
        const pd_price = document.querySelector('[id="pd-applied-price-' + `${productId}` + '"]').value;
        cartPdPlusMinusInit(pd_type, pdPlusBtn, pdMinusBtn, productId, pd_price);
    });


    const productIdOptionSelectAll = document.querySelectorAll(".uk-select");
    productIdOptionSelectAll.forEach(function (optionSelect){
        // option select count change
        optionSelect.addEventListener("change", function (e){
            let dataProductId = optionSelect.getAttribute("data-product-id");
            console.log(dataProductId)
            const selectContainer = document.querySelector('[data-container-product-id="' + `${dataProductId}` + '"]');
            e.preventDefault();
            let optionId = e.target.value;
            if (optionId !== "none") {
                let formData = new FormData();
                formData.append("_id", optionId);
                formData.append("_get", "get_option");
                let request = $.ajax({
                    url: optionSelectAjax,
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
                            if (response.pd_id && response._id && response._title && response._price) {
                                cartInsertSelectOption(optionSelect, selectContainer, response.pd_id, response._id, response._title, response._price);
                                const opPlusBtn = document.querySelector('[data-plus-id="op-plus-' + `${response._id}` + '"]');
                                const opMinusBtn = document.querySelector('[data-minus-id="op-minus-' + `${response._id}` + '"]');
                                const _type = "option";
                                cartPdOpTotalPriceCalc(response.pd_id);
                                cartOpPlusMinusInit(_type, opPlusBtn, opMinusBtn, response.pd_id, response._id, response._price);

                                const orderChangeModal = document.querySelector('[id="order-change-modal-' + `${response.pd_id}` + '"]');
                                const productId = response.pd_id;//orderChangeModal.getAttribute("data-change-product-id");
                                let cartUpdateAjaxBtn = orderChangeModal.querySelector('[data-ajax-btn-id="' + `${productId}` + '"]');
                                cartUpdateAjaxBtn.addEventListener("click", function (e) {
                                    const cartId = document.querySelector("#cart-id").value;
                                    const pdId = cartUpdateAjaxBtn.getAttribute("data-ajax-btn-id");
                                    let orderChangeModal = document.querySelector('[data-change-pd-id="' + `${pdId}` + '"]')
                                    const opSelectInsertAll = orderChangeModal.querySelectorAll('[data-insert-product-id="' + `${pdId}` + '"]');
                                    cartUpdateAjax(cartId, pdId, opSelectInsertAll);

                                }, false);

                                const newOpCancelBtnAll = document.querySelectorAll(".new.op-cancel");
                                newOpCancelBtnAll.forEach(function (newOpCancelBtn, idx) {
                                    newOpCancelBtn.addEventListener("click", function (e) {
                                        const cartId = document.querySelector("#cart-id").value;
                                        const optionId = newOpCancelBtn.parentElement.getAttribute("data-option-id");
                                        const PdId = newOpCancelBtn.parentElement.getAttribute("data-insert-product-id");
                                        const hiddenTotalPriceInput = document.querySelector('[id="total-price-' + `${PdId}` + '"]');
                                        const TotalPriceSpan = document.querySelector('[class="total-price-' + `${PdId}` + '"]');

                                        const opTotalPrice = document.querySelector('[id="op-total-price-' + `${optionId}` + '"]').value;
                                        let oldTotalPrice = hiddenTotalPriceInput.value;

                                        if (idx === 0) { // loop 를 한번만 돌리기 위해서...합계금액을 두번 계산하기 때문
                                            hiddenTotalPriceInput.value = oldTotalPrice - opTotalPrice;
                                            TotalPriceSpan.innerHTML = intComma(oldTotalPrice - opTotalPrice);
                                        }



                                    }, false);
                                });


                            }
                            if (response._data_r) {
                                console.log("data_r", response._data_r)
                            }
                        }
                    },
                    error: function (err) {
                        alert('내부 오류가 발생하였습니다.\n' + err);
                    }
                });
            }

        });
    });

    const opSelectInsertAll = document.querySelectorAll(".op-select-insert");
    opSelectInsertAll.forEach(function (opSelectInsert){
        const productId = opSelectInsert.getAttribute("data-insert-product-id");
        const optionId = opSelectInsert.getAttribute("data-option-id");
        const opPlusBtn = document.querySelector('[data-plus-id="op-plus-' + `${optionId}` + '"]');
        const opMinusBtn = document.querySelector('[data-minus-id="op-minus-' + `${optionId}` + '"]');
        const _type = "option";
        const optionPrice = document.querySelector('[id="op-price-' + `${optionId}` + '"]').value;
        cartOpPlusMinusInit(_type, opPlusBtn, opMinusBtn, productId, optionId, optionPrice);

        let OpCancelBtn = opSelectInsert.querySelector('[data-cancel-id="' + `${optionId}` + '"]');
        OpCancelBtn.addEventListener("click", function (e){
            const cartId = document.querySelector("#cart-id").value;
            const PdId = OpCancelBtn.parentElement.getAttribute("data-insert-product-id");
            const optionId = OpCancelBtn.parentElement.getAttribute("data-option-id");
            let formData = new FormData();
            formData.append("cart_id", cartId);
            formData.append("product_id", PdId);
            formData.append("option_id", optionId);

            let request = $.ajax({
                url: cartOptionDeleteAjax,
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
                        console.log("cancel success", response._success)
                        const hiddenTotalPriceInput = document.querySelector('[id="total-price-' + `${PdId}` + '"]');
                        const TotalPriceSpan = document.querySelector('[class="total-price-' + `${PdId}` + '"]');

                        const opTotalPrice = document.querySelector('[id="op-total-price-' + `${optionId}` + '"]').value;
                        let oldTotalPrice = hiddenTotalPriceInput.value

                        hiddenTotalPriceInput.value = oldTotalPrice - opTotalPrice;
                        TotalPriceSpan.innerHTML = intComma(oldTotalPrice - opTotalPrice);

                    }
                },
                error: function (err) {
                    alert('내부 오류가 발생하였습니다.\n' + err);
                }
            });

        }, false);
    });

    const cartProductContainerAll = document.querySelectorAll(".cart-product-container");
    cartProductContainerAll.forEach(function (cartProductContainer){
        const productId = cartProductContainer.getAttribute("data-cart-product-id");

        let cartUpdateAjaxBtn = cartProductContainer.querySelector('[data-ajax-btn-id="' + `${productId}` + '"]');
        cartUpdateAjaxBtn.addEventListener("click", function (e) {
            const cartId = document.querySelector("#cart-id").value;
            const pdId = cartUpdateAjaxBtn.getAttribute("data-ajax-btn-id");
            let orderChangeModal = document.querySelector('[data-change-pd-id="' + `${productId}` + '"]')
            const opSelectInsertAll = orderChangeModal.querySelectorAll('[data-insert-product-id="' + `${productId}` + '"]');

            cartUpdateAjax(cartId, pdId, opSelectInsertAll);

        }, false);
    });

    document.addEventListener("click", function (e){
        let target = e.target;
        if (target.classList.contains("del-btn")) {
            const cartId = document.querySelector("#cart-id").value;
            let PdId = target.getAttribute("data-del-btn-pd-id");
            const orderDeleteModal = document.querySelector('[id="order-delete-modal-' + `${PdId}` + '"]');
            const cartProductDeleteBtn = document.querySelector('[id="product-delete-btn-' + `${PdId}` + '"]');
            cartProductDeleteBtn.addEventListener("click", function (e){
                cartProductDelete(cartId, PdId);
            }, false);
        }
    }, false);

    const checkAllBox = document.querySelector("#all-check");
    const checkBoxList = document.querySelectorAll(".single");
    checkAllBox.addEventListener("change", function (e) {
        e.preventDefault();
        for (let i = 0; i < checkBoxList.length; i++) {
            checkBoxList[i].checked = this.checked;
        }
    });

    Array.from(checkBoxList).forEach(function (checkBox) {
        checkBox.addEventListener("change", function (e) {
            checkAllBox.checked = false;
        });
    });

    const checkedDeleteBtn = document.querySelector("#checked-delete-btn");
    checkedDeleteBtn.addEventListener("click", function (e) {
        e.preventDefault();
        Array.from(checkBoxList).forEach(function (checkBox) {
            if (checkBox.checked) {
                const cartId = document.querySelector("#cart-id").value;
                let PdId = Number(checkBox.getAttribute("id"));
                cartProductDelete(cartId, PdId);
                checkAllBox.checked = false;
            }
        });
    });




}

function cartProductDelete(cartId, PdId){
    let formData = new FormData();
    formData.append("cart_id", cartId);
    formData.append("product_id", PdId);

    let request = $.ajax({
        url: cartProductDeleteAjax,
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
                console.log("success", response._success)
                const cartProductContainer = document.querySelector('[data-cart-product-id="' + `${PdId}` + '"]');
                cartProductContainer.remove();
                const cartProduct = document.querySelector(".cart-product.bg-100.padding10");
                const existingNewDiv = cartProduct.querySelector(".main-width.mb-20");
                if (existingNewDiv === null) {
                    let newDiv = `<div class="main-width mb-20">
                                     카트에 담긴게 없습니다.
                                  </div>`;
                    cartProduct.insertAdjacentHTML('afterbegin', newDiv);
                }


                const cartTotalPriceSpan = document.querySelector("#cart_total_price");
                const cartPayPriceSpan = document.querySelector("#cart_pay_price");
                cartTotalPriceSpan.innerHTML = intComma(response.cart_total_price);
                cartPayPriceSpan.innerHTML = intComma(response.cart_total_price);
            }
        },
        error: function (err) {
            alert('내부 오류가 발생하였습니다.\n' + err);
        }
    });
}


function cartUpdateAjax(cartId, pdId, opSelectInsertAll) {
    const pdCount = document.querySelector('[id="pd-count-' + `${pdId}` + '"]').value;
    const pdTotalPrice = document.querySelector('[id="pd-total-price-' + `${pdId}` + '"]').value;

    let optionId = [];
    let optionCount = [];
    let optionTotalPrice = [];
    opSelectInsertAll.forEach(function (opSelectInsert, idx) {
        let opId = opSelectInsert.getAttribute("data-option-id");
        optionId.push(opId);//opSelectInsert.querySelector('[id="data-op-id-' + `${opId}` + '"]').value);
        optionCount.push(opSelectInsert.querySelector('[id="op-count-' + `${opId}` + '"]').value);
        optionTotalPrice.push(opSelectInsert.querySelector('[id="op-total-price-' + `${opId}` + '"]').value);
    });

    let formData = new FormData();
    formData.append("cart_id", cartId);
    formData.append("product_id", pdId);
    formData.append("product_count", pdCount);
    formData.append("product_total_price", pdTotalPrice);

    for (let i = 0; i < optionId.length; i++) {
        formData.append('option_id[]', optionId[i]);
        formData.append('option_count[]', optionCount[i]);
        formData.append('option_total_price[]', optionTotalPrice[i]);
    }
    console.log(optionId)
    console.log(optionCount)
    console.log(optionTotalPrice)

    let request = $.ajax({
        url: cartUpdatAjax,
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
                window.location.reload();
            }
        },
        error: function (err) {
            alert('내부 오류가 발생하였습니다.\n' + err);
        }
    });
}

function cartInsertSelectOption (selectTag, div, pd_id, _id, title, price) {
    console.log(div)
    let oldInsertDiv = document.querySelector('[data-id="op-' + `${_id}` + '"]');
    if (oldInsertDiv) {
        alert("이미 선택한 옵션이에요!");
        selectTag.value = "none";
    }
    else {
        let newDiv = `<div class="new op-select-insert" data-option-id="${_id}" data-insert-product-id="${pd_id}" uk-alert>
                          <div class="op-title" data-id="op-${_id}">${title} / ${intComma(Number(price))}원</div>
                          <button class="new op-cancel uk-alert-close uk-close" type="button" data-cancel-id="${_id}" style="font-size: 20px">+</button>
                          <div>
                              <button class="uk-button uk-button-default op-minus" data-minus-id="op-minus-${_id}"><span uk-icon="minus"></span></button>
                              <input readonly class="uk-input uk-form-width-xsmall op" id="op-count-${_id}" name="op-count" type="text" value="1">
                              <input type="hidden" name="op-id" value="${_id}">
                              <input type="hidden" id="op-price-${_id}" value="${Number(price)}">
                              <input type="hidden" class="op-total-price" id="op-total-price-${_id}" name="op-total-price" value="${Number(price)}">
                              <button class="uk-button uk-button-default op-plus" data-plus-id="op-plus-${_id}"><span uk-icon="plus"></span></button>
                              <div class="uk-inline uk-align-right ml-0 mt-5 mb-0"><span id="op-total-price-span-${_id}">` + intComma(Number(price)) + `</span> 원</div>
                          </div>
                     </div>`;
        div.insertAdjacentHTML('afterend', newDiv);
        selectTag.value = "none";

    }
}

function cartPdPlusMinusInit (_type, plusBtn, minusBtn, _id, price) {
    let countInput = document.querySelector('[id="pd-count-' + `${_id}` + '"]');
        pdPlusMinusPrice (_type, plusBtn, minusBtn, countInput, _id, price);

}

function cartOpPlusMinusInit (_type, plusBtn, minusBtn, pd_id, op_id, price) {
    let countInput = document.querySelector('[id="op-count-' + `${op_id}` + '"]');
    opPlusMinusPrice (_type, plusBtn, minusBtn, countInput, pd_id, op_id, price);

}

function pdPlusMinusPrice (_type, plusBtn, minusBtn, countInput, _id, price) {
    let objectNum = Number(countInput.value);
    let objectPrice = price;
    plusBtn.addEventListener("click", function (e){
        console.log(e.target)
        e.preventDefault();
        objectNum += 1;
        cartPdCountPriceApply(_type, objectNum, objectPrice, _id);
    }, false);

    minusBtn.addEventListener("click", function (e){
        e.preventDefault();
        objectNum -= 1;
        if (objectNum >= 1) {
            cartPdCountPriceApply(_type, objectNum, objectPrice, _id);
        } else {
            objectNum = 1;
        }
    }, false);
}

function cartPdCountPriceApply (_type, objectNum, objectPrice, pd_id) {
    if (_type === "product") {
        let countInput = document.querySelector('[id="pd-count-' + `${pd_id}` + '"]');
        const hiddenPdTotalPriceInput = document.querySelector('[id="pd-total-price-' + `${pd_id}` + '"]');
        const pdTotalPriceSpan = document.querySelector('[id="pd-total-price-span-' + `${pd_id}` + '"]');
        countInput.value = objectNum;
        hiddenPdTotalPriceInput.value = Number(objectNum * objectPrice);
        pdTotalPriceSpan.innerText = intComma(objectNum * objectPrice);
        cartPdOpTotalPriceCalc(pd_id);
    }

}

function opPlusMinusPrice (_type, plusBtn, minusBtn, countInput, pd_id, op_id, price) {
    let objectNum = Number(countInput.value);
    let objectPrice = price;
    plusBtn.addEventListener("click", function (e){
        e.preventDefault();
        objectNum += 1;
        cartOpCountPriceApply(_type, objectNum, objectPrice, pd_id, op_id);
    }, false);

    minusBtn.addEventListener("click", function (e){
        e.preventDefault();
        objectNum -= 1;
        if (objectNum >= 1) {
            cartOpCountPriceApply(_type, objectNum, objectPrice, pd_id, op_id);
        } else {
            objectNum = 1;
        }
    }, false);
}

function cartOpCountPriceApply (_type, objectNum, objectPrice, pd_id, op_id) {
    if (_type === "option") {
        const countInput = document.querySelector('[id="op-count-' + `${op_id}` + '"]');
        const hiddenTotalPriceInput = document.querySelector('[id="op-total-price-' + `${op_id}` + '"]');
        const OpTotalPriceSpan = document.querySelector('[id="op-total-price-span-' + `${op_id}` + '"]');
        countInput.value = objectNum;
        hiddenTotalPriceInput.value = Number(objectNum * objectPrice);
        console.log(hiddenTotalPriceInput.value)
        OpTotalPriceSpan.innerText = intComma(objectNum * objectPrice);
        // countInput.value 와 hiddenTotalPriceInput.value 를 이용해 총합계 금액을 계산하고, 이것과 계산총합을 ajax 로 보낸다.

        cartPdOpTotalPriceCalc(pd_id, op_id);

    }

}

function cartPdOpTotalPriceCalc (pd_id) {
    let totalPriceHiddenInput = document.querySelector('[id="total-price-' + `${pd_id}` + '"]');
    let totalPriceSpan = document.querySelector('[class="total-price-' + `${pd_id}` + '"]');
    const pdTotalPrice = document.querySelector('[id="pd-total-price-' + `${pd_id}` + '"]').value;
    const productMatchingOptionsAll = document.querySelectorAll('[data-insert-product-id="' + `${pd_id}` + '"]');
    console.log("Number(opTotalPriceCalc())", Number(cartOpTotalPriceCalc(productMatchingOptionsAll)))
    const pdOpTotalPrice = Number(pdTotalPrice) + Number(cartOpTotalPriceCalc(productMatchingOptionsAll));
    console.log("pdOpTotalPrice()", pdOpTotalPrice);
    totalPriceHiddenInput.value = pdOpTotalPrice;
    totalPriceSpan.innerHTML = intComma(pdOpTotalPrice);
    return pdOpTotalPrice;
}

function cartOpTotalPriceCalc (matchingOptionsAll) {
    let opTotalPrice = 0;
    matchingOptionsAll.forEach(function (matchingOption){
        const optionId = matchingOption.getAttribute("data-option-id");
        const opLinePrice = matchingOption.querySelector(".op-total-price");
        let a = Number(opLinePrice.value);
        opTotalPrice += a;
    });

    return opTotalPrice;

}

function intComma (num) {
    return Number(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}