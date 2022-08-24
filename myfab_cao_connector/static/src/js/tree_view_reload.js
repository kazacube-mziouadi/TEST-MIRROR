odoo.define("myfab_cao_connector.tree_view_reload", function (require) {
    "use strict";
    var core = require('web.core');
    var QWeb = core.qweb;
    var TreeView = require("web.TreeView");

    TreeView.include({
        render_buttons: function ($node) {
            var self = this;
            this.$buttons = $(QWeb.render("TreeView.buttons", { 'widget': this, display: true }));
            this.$buttons.on('click', 'button.o-tree-button-new', this.show_all.bind(this))
            $node = $node || this.options.$buttons;
            this.$buttons.appendTo($node);
        },

        get_additionnal_datas: function (records, parent_id) {
            if (records.length > 1 && this.fields_view.arch.attrs.default_order) {
                this.order_records(records);
            }
            return this._super(records, parent_id);
        },

        show_all: function () {
            var self = this
            $.each(this.records, function (i, record) {
                if (record.has_children) {
                    var element = $("[data-id=" + record.id + "]tr")
                    if (!element[0].classList.contains("oe_open") && element[0].getAttribute("class")==undefined && record.is_open != true) {
                        record.is_open = true
                        self.get_data_async(record.id, record.mf_tree_view_sim_action_children_ids, element).then((res)=>{
                            self.show_all()
                        }).fail(() => {
                            console.error("Error show all records")
                        })
                    }else if(element[0].getAttribute("class")==""){
                        self.showcontent(element.children('td'),record.id,true)
                    }

                }
            })
        },
        // Need async version of getdata or the recursive call will be executed before getdata fills records with the new lines
        get_data_async: function (id, children_ids, $node) {
            var deferred = $.Deferred();
            var self = this;
            self.dataset.read_ids(children_ids, this.fields_list())
                .then((records) => {
                    return self.get_additionnal_datas(records, id);
                }, err => {
                    if (self.__processing_tree_click) {
                        self.__processing_tree_click[id] = false;
                    }
                })
                .then(function(records) {
                    _(records).each(function (record) {
                        record.has_children = false;
                        for (var c of self.children_field) {
                            if (record[c] && record[c].length) {
                                record.has_children = true;
                            }
                        }
                        self.records[record.id] = record;
                    });
                    var $curr_node
                    if (!$node && id != null) {
                        $curr_node = $('#treerow_' + id)
                    } else {
                        $curr_node = $node || $();
                    }
                    var children_rows = QWeb.render('TreeView.rows', {
                        'records': records,
                        'fields_view': self.fields_view.arch.children,
                        'fields': self.fields,
                        'level': $curr_node.data('level') || 0,
                        'render': self.format_tree_value,
                        'color_for': self.color_for,
                        'row_parent_id': id,
                        'self': self
                    });
                    if ($curr_node.length) {
                        $curr_node.addClass('oe_open');
                        $curr_node.after(children_rows);
                    } else {
                        self.$el.find('tbody').html(children_rows);
                    }
                    if (self.__processing_tree_click) {
                        self.__processing_tree_click[id] = false;
                    }
                    self.init_checkboxes_editable();
                    deferred.resolve();
                }).fail(() => {
                    if (self.__processing_tree_click) {
                        self.__processing_tree_click[id] = false;
                    }
                    deferred.reject()
                });
            return deferred.promise();
        },

        order_records: function (records, ordering_field = null, order_direction = null) {
            if (ordering_field === null || order_direction === null) {
                var default_order = this.fields_view.arch.attrs.default_order;
                var default_order_split = default_order.split(' ');
                if (default_order_split.length < 2) {
                    ordering_field = default_order;
                    order_direction = "asc";
                } else {
                    ordering_field = default_order_split[0];
                    order_direction = default_order_split[1];
                }
            }
            records.sort(function (a, b) {
                if (order_direction === "desc") {
                    return b[ordering_field] - a[ordering_field];
                } else {
                    return a[ordering_field] - b[ordering_field];
                }
            })
        },
        reload: function () {
            _(this.fields_view.arch.children).each(function (field) {
                if (field.attrs.modifiers && typeof field.attrs.modifiers !== "string") {
                    field.attrs.modifiers = JSON.stringify(field.attrs.modifiers);
                }
            });
            return this.load_tree(this.fields_view);
        },
        getdata: function (id, children_ids, $node) {
            var self = this;
            self.dataset.read_ids(children_ids, this.fields_list())
                .then((records) => {
                    return self.get_additionnal_datas(records, id);
                }, err => {
                    if (self.__processing_tree_click) {
                        self.__processing_tree_click[id] = false;
                    }
                })
                .then(function(records) {
                    _(records).each(function (record) {
                        record.has_children = false;
                        for (var c of self.children_field) {
                            if (record[c] && record[c].length) {
                                record.has_children = true;
                            }
                        }
                        self.records[record.id] = record;
                    });
                    var $curr_node
                    if (!$node && id != null) {
                        $curr_node = $('#treerow_' + id)
                    } else {
                        $curr_node = $node || $();
                    }
                    var children_rows = QWeb.render('TreeView.rows', {
                        'records': records,
                        'fields_view': self.fields_view.arch.children,
                        'fields': self.fields,
                        'level': $curr_node.data('level') || 0,
                        'render': self.format_tree_value,
                        'color_for': self.color_for,
                        'row_parent_id': id,
                        'self': self
                    });
                    if ($curr_node.length) {
                        $curr_node.addClass('oe_open');
                        $curr_node.after(children_rows);
                    } else {
                        self.$el.find('tbody').html(children_rows);
                    }
                    if (self.__processing_tree_click) {
                        self.__processing_tree_click[id] = false;
                    }
                    self.init_checkboxes_editable();
                }).fail(() => {
                    if (self.__processing_tree_click) {
                        self.__processing_tree_click[id] = false;
                    }
                });
        },
        init_checkboxes_editable: function() {
            var self = this;
            var $checkboxes = $(".mf_tree_view_editable .treeview-td input[type='checkbox']:not(.mf_tree_view_checkbox_listener)");
            $checkboxes = $checkboxes.filter(function() {
                return $($(this).parents("td")[0]).attr("style").length > 0;
            })
            if ($checkboxes.length > 0) {
                $checkboxes.removeAttr("disabled");
                $checkboxes.addClass("mf_tree_view_checkbox_listener");
                $checkboxes.on("click", (event) => this.click_checkbox())
            }
        },
        set_checkboxes_editable: function() {
            var self = this;
            var $checkboxes = $(".mf_tree_view_editable .treeview-td .mf_tree_view_checkbox_listener[type='checkbox']");
            if ($checkboxes.length > 0) {
                $checkboxes.removeAttr("disabled");
            }
        },
        set_checkboxes_disabled: function() {
            var $checkboxes = $(".mf_tree_view_editable .treeview-td .mf_tree_view_checkbox_listener[type='checkbox']");
            if ($checkboxes.length > 0) {
                $checkboxes.attr("disabled", "true");
            }
        },
        click_checkbox: function() {
            this.set_checkboxes_disabled();
            var self = this;
            var $clicked_checkbox = $(event.target);
            var clicked_record_dataset = $clicked_checkbox.parents("td")[0].dataset;
            var clicked_record_id = clicked_record_dataset.id;
            var clicked_field_name = clicked_record_dataset.name;
            var clicked_checkbox_is_checked = $clicked_checkbox.prop("checked");
            this.set_checkbox($clicked_checkbox, clicked_checkbox_is_checked);
            var values_to_write = {
                [clicked_field_name]: clicked_checkbox_is_checked
            };
            self.dataset.write(parseInt(clicked_record_id), values_to_write).then(result => {
                self.reload_checkboxes(clicked_field_name);
            })
        },
        set_checkbox: function($checkbox_to_toggle, value_to_set) {
            if ($checkbox_to_toggle.prop("checked") != value_to_set) {
                $checkbox_to_toggle.prop("checked", value_to_set);
            }
        },
        reload_checkboxes: function(clicked_field_name) {
            var self = this;
            var $tree_view_lines = $(".mf_tree_view_editable tr");
            var record_ids = [];
            $tree_view_lines.each(function() {
                var line_record_id = $(this).attr("data-id");
                if (line_record_id !== undefined) {
                    record_ids.push(parseInt(line_record_id));
                }
            })
            self.dataset.read_ids(record_ids, [clicked_field_name]).then(record_values_array => {
                for (var record_value_index in record_values_array) {
                    var record_value_dict = record_values_array[record_value_index]
                    var $record_checkbox = $(".mf_tree_view_editable .treeview-td[data-id='" + record_value_dict["id"] + "'] input[type='checkbox']");
                    self.set_checkbox($record_checkbox, record_value_dict[clicked_field_name]);
                }
                this.set_checkboxes_editable();
            })
        }
    })
});
