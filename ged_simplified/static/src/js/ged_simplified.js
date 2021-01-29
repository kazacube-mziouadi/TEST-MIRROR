odoo.define('module.open_file_browser', function (require) {
    "use strict";
    var ajax = require('web.ajax');

    window.addEventListener('hashchange', function() {
        var queryString = window.location.href.split("/web#")[1];
        const urlParams = new URLSearchParams(queryString);
        if (urlParams.get("model") == "res.partner" && urlParams.get("id")) {
            console.log(urlParams.get("id"));
            ajax.jsonRpc("/partner/directory_path", "call", {"partner_id" : urlParams.get("id")}).then(function(result) {
                console.log(result);
                if (result["os"].includes("Linux")) {
                    preparePartnerFormAccordingToOS("directory_id_mf_absolute_path_windows", "myfab:/" + result["partner_docs_path"])
                } else if (result["os"].includes("Windows")) {
                    preparePartnerFormAccordingToOS("directory_id_mf_absolute_path", "myfab://explorer/" + result["partner_docs_path"])
                }
            })
        }
    })

    function preparePartnerFormAccordingToOS(fieldToHide, partnerDirectoryOpenUrl) {
        const spanToHide = $('.res\\.partner__' + fieldToHide);
        const buttonOpenDirectory = $('.button_open_directory');
        $('label[field-name=' + fieldToHide + ']').parent().hide();
        $(spanToHide).parent().hide();
        $(buttonOpenDirectory).attr("href", partnerDirectoryOpenUrl);
        $(spanToHide).parent().parent().append($(buttonOpenDirectory).parent());
        $(buttonOpenDirectory).parent().css("text-align", "right");
    }
});