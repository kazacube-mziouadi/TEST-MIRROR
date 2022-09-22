odoo.define('myfab_online_help', function(require) {
    "use strict";

    var Menu = require('web.Menu');

    Menu.include({
        bind_menu: function() {
            var user_menu = $(".oe_user_menu_placeholder");
            var self = this;
            this._super.apply(this, arguments);
            user_menu.prepend(
                '<li class="oe_online_help">' +
                    '<a href="#" title="myfab Online Help">?' + 
                    '</a>' +
                '</li>'
            );
            // Bind a click event via JQuery that change the actual user's company
            $(".oe_online_help").click((e) => {
                window.open('http://srv-bron-dkr1:8080/books','_blank');                         
            });
        }
    });

    return Menu;
});