"use strict"
/*jshint esversion: 6 */
imgPreviewInit();
function imgPreviewInit() {
    // profile image
    try {
        const profileImgInput = document.querySelector("#profile_image");
        profileImgInput.addEventListener("change", function (e) {
            let _width = `100%`;
            let _height = `100%`;
            let profileImgPreviewTag = document.querySelector('#img-preview');
            previewStyle(profileImgPreviewTag, _width, _height);

            let profileImgInputFile = profileImgInput.files[0];
            console.log("profileImgInputFile", profileImgInputFile)
            imgFileReader(profileImgPreviewTag, profileImagePath, profileImgInputFile);
        }, false);
    } catch (e) {
        // console.log(e);
    }

    // business license
    try {
        const corpImgInput = document.querySelector("#corp_image");
        corpImgInput.addEventListener("change", function (e) {
            let _width = `100%`;
            let _height = `auto`;
            let corpImgPreviewTag = document.querySelector('#corp-img-preview');
            previewStyle(corpImgPreviewTag, _width, _height);

            let corpImgInputFile = corpImgInput.files[0];
            imgFileReader(corpImgPreviewTag, corpImagePath, corpImgInputFile);
        }, false);
    } catch (e) {
        // console.log(e);
    }

    // account/shopCategory cover image
    try {
        let _width = `100%`;
        let _height = `250px`;

        const coverImgInput1 = document.querySelector("#cover_image1");
        coverImgInput1.addEventListener("change", function (e) {
            let coverImgPreviewTag1 = document.querySelector('#cover-img1-preview');
            previewStyle(coverImgPreviewTag1, _width, _height);

            let coverImgInputFile1 = coverImgInput1.files[0];
            imgFileReader(coverImgPreviewTag1, image1Path, coverImgInputFile1);
        }, false);

        const coverImgInput2 = document.querySelector("#cover_image2");
        coverImgInput2.addEventListener("change", function (e) {
            let coverImgPreviewTag2 = document.querySelector('#cover-img2-preview');
            previewStyle(coverImgPreviewTag2, _width, _height);

            let coverImgInputFile2 = coverImgInput2.files[0];
            imgFileReader(coverImgPreviewTag2, image2Path, coverImgInputFile2);
        }, false);

        const coverImgInput3 = document.querySelector("#cover_image3");
        coverImgInput3.addEventListener("change", function (e) {
            let coverImgPreviewTag3 = document.querySelector('#cover-img3-preview');
            previewStyle(coverImgPreviewTag3, _width, _height);

            let coverImgInputFile3 = coverImgInput3.files[0];
            imgFileReader(coverImgPreviewTag3, image3Path, coverImgInputFile3);
        }, false);

    } catch (e) {
        // console.log(e);
    }

    // shopCategory symbol image
    try {
        const symbolImgInput = document.querySelector("#symbol_image");
        symbolImgInput.addEventListener("change", function (e) {
            let _width = `100%`;
            let _height = `100%`;
            const symbolPreviewImgTag = document.querySelector("#symbol-preview");
            previewStyle(symbolPreviewImgTag, _width, _height);

            let symbolImgInputFile = symbolImgInput.files[0];
            imgFileReader(symbolPreviewImgTag, symbolImagePath, symbolImgInputFile);
        }, false);

    } catch (e) {
        // console.log(e);
    }

}

function previewStyle(previewImgTag, _width, _height) {
    previewImgTag.style.cssText = ` width:` + _width + `;
                                height:` + _height + `;
                                object-fit:cover;
                                `;
}

function imgFileReader(previewImgTag, imgSrc, inputFile) {
    let reader = new FileReader();
    reader.addEventListener("load", function () {
        previewImgTag.src = reader.result;
    }, false);

    if (inputFile) {
        previewImgTag.classList.add('active');
        console.log(inputFile)
        reader.readAsDataURL(inputFile);
    } else {
        previewImgTag.classList.remove('active');
        previewImgTag.src = imgSrc;
        // if (previewImgTag.classList.contains('profile-cover-img')) {
        //     previewImgTag.src = imgSrc;
        // } else {
        //     previewImgTag.src = imgSrc;
        //     // window.location.reload()
        // }


    }
}


