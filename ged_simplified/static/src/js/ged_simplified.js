odoo.define('module.open_file_browser', function (require) {
    "use strict";

    if (navigator.userAgent.includes('Linux')) {
        console.log('CLIENT ON LINUX');
        var intervalId = setInterval(function() {
            const spanPathValueWindows = $('.res\\.partner__directory_id_mf_absolute_path_windows');
            if ($(spanPathValueWindows).length > 0) {
                const buttonOpenDirectory = $('.button_open_directory');
                $('label[field-name=directory_id_mf_absolute_path_windows]').parent().hide();
                $(spanPathValueWindows).parent().hide();
                $(buttonOpenDirectory).attr("href", "myfab:/" + $('.res\\.partner__directory_id_mf_absolute_path > span').html());
                $(spanPathValueWindows).parent().parent().append($(buttonOpenDirectory).parent());
                $(buttonOpenDirectory).parent().css("text-align", "right");
            }
        }, 1000)
    } else if (navigator.userAgent.includes('Windows')) {
        console.log('CLIENT ON WINDOWS')
        var intervalId = setInterval(function() {
            const spanPathValueLinux = $('.res\\.partner__directory_id_mf_absolute_path');
            if ($(spanPathValueLinux).length > 0) {
                const buttonOpenDirectory = $('.button_open_directory');
                $('label[field-name=directory_id_mf_absolute_path]').parent().hide();
                $(spanPathValueLinux).parent().hide();
                $(buttonOpenDirectory).attr("href", "myfab://explorer/" + $('.res\\.partner__directory_id_mf_absolute_path_windows > span').html());
                $(spanPathValueLinux).parent().parent().append($(buttonOpenDirectory).parent());
                $(buttonOpenDirectory).parent().css("text-align", "right");
            }
        }, 1000)
    }
});