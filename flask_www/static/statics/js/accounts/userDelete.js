document.addEventListener('DOMContentLoaded',  function () {

    const accounts_del = document.querySelector('#accounts-del');
    accounts_del.addEventListener("click", ConfirmDelete, false);

    function ConfirmDelete() {
        let confirmation = confirm("정말 탈퇴하실 건가요?");
        const CSRF_TOKEN = csrf_token;
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
                }
            }
        });
        let _id = document.querySelector('#_id').getAttribute('value');
        if (confirmation === true) {
            $.ajax({
                method: "POST",
                url: accounts_delete_url,
                data: {
                    _id: _id,
                },
                success: function () {
                    window.location.href = common_index_url
                }
            });
        }
    }



});