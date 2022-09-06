odoo.define('myfab_OnlineHelp', function (require) {
"use strict";

var core = require('web.core');
var View = require('web.View');
var Model = require('web.DataModel');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var session = require('web.session');

var QWeb = core.qweb;

var _lt = core._lt;

/* View used to display esn notification and message */
var myfab_OnlineHelp = View.extend({
    template: 'myfab_OnlineHelp',
    accesskey: "H",
    display_name: _lt("Help"),
    icon: 'fa-help',
    view_type: "help",

    events: {
        "click .op_mf_menu_button": "on_button_hide",
    },

    init: function (parent, dataset, view_id, options) {
        this._super(parent, dataset, view_id, options);
        this.dataset = dataset;
        this.view_id = view_id || false;
        this.ViewManager = parent;
        this.data_loading = false;

        this.model= new Model(this.dataset.model);
    },
    start: function() {
        this._super.apply(this, arguments);
    },
    do_search: function (domain, context, group_by, offset = 0) {
        var limit = context && context.limit || 20;
        // Prevent loading the data twice at the same time
        if (!this.data_loading) {
            var self = this;
            this.data_loading = true;
            _.each(this.$el.find('.op_esn_view_container'), function(val, key){
               $(val).empty();
            });
            this.$el.find('.op_esn_view_date_category').hide();

            if (this.dataset.model == "esn.notification") {
                var fields = [
                    'state', 'name', 'linked_object_id', 'record_name', 'author_id', 'message_id', 'create_date', 
                    'message', 'message_type', 'parent_id', 'tag_ids', 'recipient_ids', 'attachment_ids'
                ];
                this.model.query(fields).filter(domain).limit(limit).offset(offset).all().done(function (notifications) {
                    if (self.options && self.options.pager) {
                        self.handlePager(notifications.length, domain, context, group_by, offset);
                    }
                    _.each(notifications, function(val, key) {
                        var notification = new OP_Notification(self, val);
                        notification.prependTo(self.$el.find('.op_esn_view_'+notification.Message.date_category).find('.op_esn_view_container'));
                        self.$el.find('.op_esn_view_'+notification.Message.date_category).show();
                    });
                    self.data_loading = false;
                });
            } else if (this.dataset.model == "esn.message") {
                domain.push(["parent_id", "=", false]);
                var fields = [
                    'change_status_date', 'create_date', 'parent_id', 'author_id', 'message_type', 'childs_ids',
                    'tag_ids', 'recipient_ids', 'attachment_ids', 'message', 'linked_object_id'
                ];
                this.model.query(fields).filter(domain).limit(limit).offset(offset).all().done(function (messages) {
                    if (self.options && self.options.pager) {
                        self.handlePager(messages.length, domain, context, group_by, offset);
                    }
                    _.each(messages, function(val, key) {
                        var message = new Message(self, val);
                        message.prependTo(self.$el.find('.op_esn_view_'+message.date_category).find('.op_esn_view_container'));
                        self.$el.find('.op_esn_view_'+message.date_category).show();
                    });
                    self.data_loading = false;
                });
            }
        }
   },

   do_show: function() {
       // Used to update the url
       this.do_push_state({});
       this.$el.find('.op_esn_view_legend').text(this.title);
       return this._super();
   },

    on_button_hide: function (event) {
        if ($(event.target).text() == _lt("Hide")) {
            $(event.target.parentNode.parentNode).find('.op_esn_view_container').hide();
            $(event.target).text(_lt("Show"));
        } else {
            $(event.target.parentNode.parentNode).find('.op_esn_view_container').show();
            $(event.target).text(_lt("Hide"));
        }
    },

    on_dataset_changed: function (domain = null) {
        /** Used to update the dataset when a notification state is changed
            FIXME: not reload all notification but only the changed one */
        if(domain)
        {
            this.domain = domain;
        }
        this.do_search(this.domain, this.context, this.group_by);
    },
    handlePager:function (queryLength, domain, context, group_by, offset) {
        var limit = context && context.limit || 20;
        var self = this;
        this.model.query(['id'])
        .filter(domain)
        .count()
        .then(counter=>{
            if (!this.ViewManager.object_model)
            {
                //create pager
                $('.oe-cp-pager').html('');
                $(QWeb.render('ActivityFeedView.pager', { 'widget': this })).appendTo('.oe-cp-pager');
                $(".oe_list_pager_state").on('click',e=>{
                    var sec_rule = this.ViewManager && this.ViewManager.action && this.ViewManager.action.security_rule;
                    var is_admin = sec_rule === true || (_.isObject(sec_rule) && sec_rule.is_admin);
                    $(".oe_list_pager_state").off();
                    $(".oe_list_pager_state").html($(QWeb.render('ActivityFeedView.options', { 'widget': this, 'is_admin': is_admin })));
                    $(".oe_list_pager_state select").val(
                        this.dataset && this.dataset._model && this.dataset._model._context && this.dataset._model._context.limit || 20
                    );
                    $(".oe_list_pager_state select").on('blur',e=>{
                        context.limit =  parseInt($(".oe_list_pager_state select").val());
                        self.do_search(domain, context, group_by,offset);
                    });
                });
                if(queryLength < counter)
                {
                    //activate pagers buttons
                    $("a[data-pager-action='previous']").on('click', ()=>{
                        if((offset-limit)<0)
                            {
                                self.do_search(domain, context, group_by,counter-limit);
                            }
                            else
                            {
                                self.do_search(domain, context, group_by,offset-limit);
                            }
                    });
                    $("a[data-pager-action='next']").on('click', ()=>{
                        if((offset+limit)>counter)
                        {
                            self.do_search(domain, context, group_by,0);
                        }
                        else
                        {
                            self.do_search(domain, context, group_by,offset+limit);
                        }
                    });    
                }
                $('.oe_list_pager_state').html((offset+1)+' - '+(offset+queryLength)+' '+ _lt('_of')+' '+counter);
            }
        });
    }
});



/* Button and Counter in the navbar for the My Action module */
var ActionMenuWidget = Widget.extend({
    template: "myfab_OnlineHelp.MenuWidget",

    events: {
        "click .op_mf_menu_button": "on_click",
    },

    init: function (parent) {
        this._super(parent);
    },

    start: function () {
        var self = this;

        this.$el.find('.fa').addClass("fa-help");

        // Update the counter when the user click on the nav bar
        this.$el.closest('#oe_main_menu_navbar').on("click", this.on_navbar_click);
    },

    // Open the calendar view with the user's actions
    on_click: function (event) {
        $('#homepage').hide();
        $('.oe_webclient').show();
        this.do_action('base_openprod.action_user_my_action');
    }
});

SystrayMenu.Items.push(ActionMenuWidget);
core.view_registry.add('help', myfab_OnlineHelp);

return myfab_OnlineHelp;
});
