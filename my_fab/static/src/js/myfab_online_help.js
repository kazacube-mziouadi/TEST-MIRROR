odoo.define('myfab_online_help', function(require) {
    "use strict";

    var Menu = require('web.Menu');

    Menu.include({
        bind_menu: function() {
            var systray = $(".oe_systray");
            this._super.apply(this, arguments);

            // TODO : ajouter l'icone class="fa fa-circle-question"
            systray.prepend(
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