openerp.green_erp_arulmani_hrm = function (instance) {
	var _t = instance.web._t,
	   _lt = instance.web._lt;
	var QWeb = instance.web.qweb;

instance.web.FormView = instance.web.View.extend(instance.web.form.FieldManagerMixin, {
    /**
     * Indicates that this view is not searchable, and thus that no search
     * view should be displayed (if there is one active).
     */
    searchable: false,
    template: "FormView",
    display_name: _lt('Form'),
    view_type: "form",
    /**
     * @constructs instance.web.FormView
     * @extends instance.web.View
     *
     * @param {instance.web.Session} session the current openerp session
     * @param {instance.web.DataSet} dataset the dataset this view will work with
     * @param {String} view_id the identifier of the OpenERP view object
     * @param {Object} options
     *                  - resize_textareas : [true|false|max_height]
     *
     * @property {instance.web.Registry} registry=instance.web.form.widgets widgets registry for this form view instance
     */
    init: function(parent, dataset, view_id, options) {
        var self = this;
        this._super(parent);
        this.ViewManager = parent;
        this.set_default_options(options);
        this.dataset = dataset;
        this.model = dataset.model;
        this.view_id = view_id || false;
        this.fields_view = {};
        this.fields = {};
        this.fields_order = [];
        this.datarecord = {};
        this.default_focus_field = null;
        this.default_focus_button = null;
        this.fields_registry = instance.web.form.widgets;
        this.tags_registry = instance.web.form.tags;
        this.widgets_registry = instance.web.form.custom_widgets;
        this.has_been_loaded = $.Deferred();
        this.translatable_fields = [];
        _.defaults(this.options, {
            "not_interactible_on_create": false,
            "initial_mode": "view",
            "disable_autofocus": false,
            "footer_to_buttons": false,
        });
        this.is_initialized = $.Deferred();
        this.mutating_mutex = new $.Mutex();
        this.on_change_list = [];
        this.save_list = [];
        this.reload_mutex = new $.Mutex();
        this.__clicked_inside = false;
        this.__blur_timeout = null;
        this.rendering_engine = new instance.web.form.FormRenderingEngine(this);
        self.set({actual_mode: self.options.initial_mode});
        this.has_been_loaded.done(function() {
            self.on("change:actual_mode", self, self.check_actual_mode);
            self.check_actual_mode();
            self.on("change:actual_mode", self, self.init_pager);
            self.init_pager();
        });
        self.on("load_record", self, self.load_record);
        instance.web.bus.on('clear_uncommitted_changes', this, function(e) {
            if (!this.can_be_discarded()) {
                e.preventDefault();
            }
        });
    },
    view_loading: function(r) {
        return this.load_form(r);
    },
    destroy: function() {
        _.each(this.get_widgets(), function(w) {
            w.off('focused blurred');
            w.destroy();
        });
        if (this.$el) {
            this.$el.off('.formBlur');
        }
        this._super();
    },
    load_form: function(data) {
        var self = this;
        if (!data) {
            throw new Error(_t("No data provided."));
        }
        if (this.arch) {
            throw "Form view does not support multiple calls to load_form";
        }
        this.fields_order = [];
        this.fields_view = data;

        this.rendering_engine.set_fields_registry(this.fields_registry);
        this.rendering_engine.set_tags_registry(this.tags_registry);
        this.rendering_engine.set_widgets_registry(this.widgets_registry);
        this.rendering_engine.set_fields_view(data);
        var $dest = this.$el.hasClass("oe_form_container") ? this.$el : this.$el.find('.oe_form_container');
        this.rendering_engine.render_to($dest);

        this.$el.on('mousedown.formBlur', function () {
            self.__clicked_inside = true;
        });

        this.$buttons = $(QWeb.render("FormView.buttons", {'widget':self}));
        if (this.options.$buttons) {
            this.$buttons.appendTo(this.options.$buttons);
        } else {
            this.$el.find('.oe_form_buttons').replaceWith(this.$buttons);
        }
        this.$buttons.on('click', '.oe_form_button_create',
                         this.guard_active(this.on_button_create));
        this.$buttons.on('click', '.oe_form_button_edit',
                         this.guard_active(this.on_button_edit));
        this.$buttons.on('click', '.oe_form_button_save',
                         this.guard_active(this.on_button_save));
        this.$buttons.on('click', '.oe_form_button_cancel',
                         this.guard_active(this.on_button_cancel));
        if (this.options.footer_to_buttons) {
            this.$el.find('footer').appendTo(this.$buttons);
        }

        this.$sidebar = this.options.$sidebar || this.$el.find('.oe_form_sidebar');
        if (!this.sidebar && this.options.$sidebar) {
            this.sidebar = new instance.web.Sidebar(this);
            this.sidebar.appendTo(this.$sidebar);
            if (this.fields_view.toolbar) {
                this.sidebar.add_toolbar(this.fields_view.toolbar);
            }
            this.sidebar.add_items('other', _.compact([
                self.is_action_enabled('delete') && { label: _t('Delete'), callback: self.on_button_delete },
                //self.is_action_enabled('create') && { label: _t('Duplicate'), callback: self.on_button_duplicate }
            ]));
        }

        this.has_been_loaded.resolve();

        // Add bounce effect on button 'Edit' when click on readonly page view.
        this.$el.find(".oe_form_group_row,.oe_form_field,label").on('click', function (e) {
            if(self.get("actual_mode") == "view") {
                var $button = self.options.$buttons.find(".oe_form_button_edit");
                $button.openerpBounce();
                e.stopPropagation();
                instance.web.bus.trigger('click', e);
            }
        });
        //bounce effect on red button when click on statusbar.
        this.$el.find(".oe_form_field_status:not(.oe_form_status_clickable)").on('click', function (e) {
            if((self.get("actual_mode") == "view")) {
                var $button = self.$el.find(".oe_highlight:not(.oe_form_invisible)").css({'float':'left','clear':'none'});
                $button.openerpBounce();
                e.stopPropagation();
            }
         });
        this.trigger('form_view_loaded', data);
        return $.when();
    },
    widgetFocused: function() {
        // Clear click flag if used to focus a widget
        this.__clicked_inside = false;
        if (this.__blur_timeout) {
            clearTimeout(this.__blur_timeout);
            this.__blur_timeout = null;
        }
    },
    widgetBlurred: function() {
        if (this.__clicked_inside) {
            // clicked in an other section of the form (than the currently
            // focused widget) => just ignore the blurring entirely?
            this.__clicked_inside = false;
            return;
        }
        var self = this;
        // clear timeout, if any
        this.widgetFocused();
        this.__blur_timeout = setTimeout(function () {
            self.trigger('blurred');
        }, 0);
    },

    do_load_state: function(state, warm) {
        if (state.id && this.datarecord.id != state.id) {
            if (this.dataset.get_id_index(state.id) === null) {
                this.dataset.ids.push(state.id);
            }
            this.dataset.select_id(state.id);
            this.do_show({ reload: warm });
        }
    },
    /**
     *
     * @param {Object} [options]
     * @param {Boolean} [mode=undefined] If specified, switch the form to specified mode. Can be "edit" or "view".
     * @param {Boolean} [reload=true] whether the form should reload its content on show, or use the currently loaded record
     * @return {$.Deferred}
     */
    do_show: function (options) {
        var self = this;
        options = options || {};
        if (this.sidebar) {
            this.sidebar.$el.show();
        }
        if (this.$buttons) {
            this.$buttons.show();
        }
        this.$el.show().css({
            opacity: '0',
            filter: 'alpha(opacity = 0)'
        });
        this.$el.add(this.$buttons).removeClass('oe_form_dirty');

        var shown = this.has_been_loaded;
        if (options.reload !== false) {
            shown = shown.then(function() {
                if (self.dataset.index === null) {
                    // null index means we should start a new record
                    return self.on_button_new();
                }
                var fields = _.keys(self.fields_view.fields);
                fields.push('display_name');
                return self.dataset.read_index(fields, {
                    context: { 'bin_size': true, 'future_display_name' : true }
                }).then(function(r) {
                    self.trigger('load_record', r);
                });
            });
        }
        return shown.then(function() {
            self._actualize_mode(options.mode || self.options.initial_mode);
            self.$el.css({
                opacity: '1',
                filter: 'alpha(opacity = 100)'
            });
        });
    },
    do_hide: function () {
        if (this.sidebar) {
            this.sidebar.$el.hide();
        }
        if (this.$buttons) {
            this.$buttons.hide();
        }
        if (this.$pager) {
            this.$pager.hide();
        }
        this._super();
    },
    load_record: function(record) {
        var self = this, set_values = [];
        if (!record) {
            this.set({ 'title' : undefined });
            this.do_warn(_t("Form"), _t("The record could not be found in the database."), true);
            return $.Deferred().reject();
        }
        this.datarecord = record;
        this._actualize_mode();
        this.set({ 'title' : record.id ? record.display_name : _t("New") });

        _(this.fields).each(function (field, f) {
            field._dirty_flag = false;
            field._inhibit_on_change_flag = true;
            var result = field.set_value(self.datarecord[f] || false);
            field._inhibit_on_change_flag = false;
            set_values.push(result);
        });
        return $.when.apply(null, set_values).then(function() {
            if (!record.id) {
                // New record: Second pass in order to trigger the onchanges
                // respecting the fields order defined in the view
                _.each(self.fields_order, function(field_name) {
                    if (record[field_name] !== undefined) {
                        var field = self.fields[field_name];
                        field._dirty_flag = true;
                        self.do_onchange(field);
                    }
                });
            }
            self.on_form_changed();
            self.rendering_engine.init_fields();
            self.is_initialized.resolve();
            self.do_update_pager(record.id == null);
            if (self.sidebar) {
               self.sidebar.do_attachement_update(self.dataset, self.datarecord.id);
            }
            if (record.id) {
                self.do_push_state({id:record.id});
            } else {
                self.do_push_state({});
            }
            self.$el.add(self.$buttons).removeClass('oe_form_dirty');
            self.autofocus();
        });
    },
    /**
     * Loads and sets up the default values for the model as the current
     * record
     *
     * @return {$.Deferred}
     */
    load_defaults: function () {
        var self = this;
        var keys = _.keys(this.fields_view.fields);
        if (keys.length) {
            return this.dataset.default_get(keys).then(function(r) {
                self.trigger('load_record', r);
            });
        }
        return self.trigger('load_record', {});
    },
    on_form_changed: function() {
        this.trigger("view_content_has_changed");
    },
    do_notify_change: function() {
        this.$el.add(this.$buttons).addClass('oe_form_dirty');
    },
    execute_pager_action: function(action) {
        if (this.can_be_discarded()) {
            switch (action) {
                case 'first':
                    this.dataset.index = 0;
                    break;
                case 'previous':
                    this.dataset.previous();
                    break;
                case 'next':
                    this.dataset.next();
                    break;
                case 'last':
                    this.dataset.index = this.dataset.ids.length - 1;
                    break;
            }
            this.reload();
            this.trigger('pager_action_executed');
        }
    },
    init_pager: function() {
        var self = this;
        if (this.$pager)
            this.$pager.remove();
        if (this.get("actual_mode") === "create")
            return;
        this.$pager = $(QWeb.render("FormView.pager", {'widget':self})).hide();
        if (this.options.$pager) {
            this.$pager.appendTo(this.options.$pager);
        } else {
            this.$el.find('.oe_form_pager').replaceWith(this.$pager);
        }
        this.$pager.on('click','a[data-pager-action]',function() {
            var action = $(this).data('pager-action');
            self.execute_pager_action(action);
        });
        this.do_update_pager();
    },
    do_update_pager: function(hide_index) {
        this.$pager.toggle(this.dataset.ids.length > 1);
        if (hide_index) {
            $(".oe_form_pager_state", this.$pager).html("");
        } else {
            $(".oe_form_pager_state", this.$pager).html(_.str.sprintf(_t("%d / %d"), this.dataset.index + 1, this.dataset.ids.length));
        }
    },
    parse_on_change: function (on_change, widget) {
        var self = this;
        var onchange = _.str.trim(on_change);
        var call = onchange.match(/^\s?(.*?)\((.*?)\)\s?$/);
        if (!call) {
            throw new Error(_.str.sprintf( _t("Wrong on change format: %s"), onchange ));
        }

        var method = call[1];
        if (!_.str.trim(call[2])) {
            return {method: method, args: []}
        }

        var argument_replacement = {
            'False': function () {return false;},
            'True': function () {return true;},
            'None': function () {return null;},
            'context': function () {
                return new instance.web.CompoundContext(
                        self.dataset.get_context(),
                        widget.build_context() ? widget.build_context() : {});
            }
        };
        var parent_fields = null;
        var args = _.map(call[2].split(','), function (a, i) {
            var field = _.str.trim(a);

            // literal constant or context
            if (field in argument_replacement) {
                return argument_replacement[field]();
            }
            // literal number
            if (/^-?\d+(\.\d+)?$/.test(field)) {
                return Number(field);
            }
            // form field
            if (self.fields[field]) {
                var value_ = self.fields[field].get_value();
                return value_ == null ? false : value_;
            }
            // parent field
            var splitted = field.split('.');
            if (splitted.length > 1 && _.str.trim(splitted[0]) === "parent" && self.dataset.parent_view) {
                if (parent_fields === null) {
                    parent_fields = self.dataset.parent_view.get_fields_values();
                }
                var p_val = parent_fields[_.str.trim(splitted[1])];
                if (p_val !== undefined) {
                    return p_val == null ? false : p_val;
                }
            }
            // string literal
            var first_char = field[0], last_char = field[field.length-1];
            if ((first_char === '"' && last_char === '"')
                || (first_char === "'" && last_char === "'")) {
                return field.slice(1, -1);
            }

            throw new Error("Could not get field with name '" + field +
                            "' for onchange '" + onchange + "'");
        });

        return {
            method: method,
            args: args
        };
    },
    do_onchange: function(widget, processed) {
        var self = this;
        this.on_change_list = [{widget: widget, processed: processed}].concat(this.on_change_list);
        return this._process_operations();
    },
    _process_onchange: function(on_change_obj) {
        var self = this;
        var widget = on_change_obj.widget;
        var processed = on_change_obj.processed;
        try {
            var def;
            processed = processed || [];
            processed.push(widget.name);
            var on_change = widget.node.attrs.on_change;
            if (on_change) {
                var change_spec = self.parse_on_change(on_change, widget);
                var ids = [];
                if (self.datarecord.id && !instance.web.BufferedDataSet.virtual_id_regex.test(self.datarecord.id)) {
                    // In case of a o2m virtual id, we should pass an empty ids list
                    ids.push(self.datarecord.id);
                }
                def = self.alive(new instance.web.Model(self.dataset.model).call(
                    change_spec.method, [ids].concat(change_spec.args)));
            } else {
                def = $.when({});
            }
            return def.then(function(response) {
                if (widget.field['change_default']) {
                    var fieldname = widget.name;
                    var value_;
                    if (response.value && (fieldname in response.value)) {
                        // Use value from onchange if onchange executed
                        value_ = response.value[fieldname];
                    } else {
                        // otherwise get form value for field
                        value_ = self.fields[fieldname].get_value();
                    }
                    var condition = fieldname + '=' + value_;

                    if (value_) {
                        return self.alive(new instance.web.Model('ir.values').call(
                            'get_defaults', [self.model, condition]
                        )).then(function (results) {
                            if (!results.length) {
                                return response;
                            }
                            if (!response.value) {
                                response.value = {};
                            }
                            for(var i=0; i<results.length; ++i) {
                                // [whatever, key, value]
                                var triplet = results[i];
                                response.value[triplet[1]] = triplet[2];
                            }
                            return response;
                        });
                    }
                }
                return response;
            }).then(function(response) {
                return self.on_processed_onchange(response, processed);
            });
        } catch(e) {
            console.error(e);
            instance.webclient.crashmanager.show_message(e);
            return $.Deferred().reject();
        }
    },
    on_processed_onchange: function(result, processed) {
        try {
        if (result.value) {
            this._internal_set_values(result.value, processed);
        }
        if (!_.isEmpty(result.warning)) {
            instance.web.dialog($(QWeb.render("CrashManager.warning", result.warning)), {
                title:result.warning.title,
                modal: true,
                buttons: [
                    {text: _t("Ok"), click: function() { $(this).dialog("close"); }}
                ]
            });
        }

        var fields = this.fields;
        _(result.domain).each(function (domain, fieldname) {
            var field = fields[fieldname];
            if (!field) { return; }
            field.node.attrs.domain = domain;
        });

        return $.Deferred().resolve();
        } catch(e) {
            console.error(e);
            instance.webclient.crashmanager.show_message(e);
            return $.Deferred().reject();
        }
    },
    _process_operations: function() {
        var self = this;
        return this.mutating_mutex.exec(function() {
            function iterate() {
                var on_change_obj = self.on_change_list.shift();
                if (on_change_obj) {
                    return self._process_onchange(on_change_obj).then(function() {
                        return iterate();
                    });
                }
                var defs = [];
                _.each(self.fields, function(field) {
                    defs.push(field.commit_value());
                });
                var args = _.toArray(arguments);
                return $.when.apply($, defs).then(function() {
                    if (self.on_change_list.length !== 0) {
                        return iterate();
                    }
                    var save_obj = self.save_list.pop();
                    if (save_obj) {
                        return self._process_save(save_obj).then(function() {
                            save_obj.ret = _.toArray(arguments);
                            return iterate();
                        }, function() {
                            save_obj.error = true;
                        });
                    }
                    return $.when();
                });
            };
            return iterate();
        });
    },
    _internal_set_values: function(values, exclude) {
        exclude = exclude || [];
        for (var f in values) {
            if (!values.hasOwnProperty(f)) { continue; }
            var field = this.fields[f];
            // If field is not defined in the view, just ignore it
            if (field) {
                var value_ = values[f];
                if (field.get_value() != value_) {
                    field._inhibit_on_change_flag = true;
                    field.set_value(value_);
                    field._inhibit_on_change_flag = false;
                    field._dirty_flag = true;
                    if (!_.contains(exclude, field.name)) {
                        this.do_onchange(field, exclude);
                    }
                }
            }
        }
        this.on_form_changed();
    },
    set_values: function(values) {
        var self = this;
        return this.mutating_mutex.exec(function() {
            self._internal_set_values(values);
        });
    },
    /**
     * Ask the view to switch to view mode if possible. The view may not do it
     * if the current record is not yet saved. It will then stay in create mode.
     */
    to_view_mode: function() {
        this._actualize_mode("view");
    },
    /**
     * Ask the view to switch to edit mode if possible. The view may not do it
     * if the current record is not yet saved. It will then stay in create mode.
     */
    to_edit_mode: function() {
        this._actualize_mode("edit");
    },
    /**
     * Ask the view to switch to a precise mode if possible. The view is free to
     * not respect this command if the state of the dataset is not compatible with
     * the new mode. For example, it is not possible to switch to edit mode if
     * the current record is not yet saved in database.
     *
     * @param {string} [new_mode] Can be "edit", "view", "create" or undefined. If
     * undefined the view will test the actual mode to check if it is still consistent
     * with the dataset state.
     */
    _actualize_mode: function(switch_to) {
        var mode = switch_to || this.get("actual_mode");
        if (! this.datarecord.id) {
            mode = "create";
        } else if (mode === "create") {
            mode = "edit";
        }
        this.set({actual_mode: mode});
    },
    check_actual_mode: function(source, options) {
        var self = this;
        if(this.get("actual_mode") === "view") {
            self.$el.removeClass('oe_form_editable').addClass('oe_form_readonly');
            self.$buttons.find('.oe_form_buttons_edit').hide();
            self.$buttons.find('.oe_form_buttons_view').show();
            self.$sidebar.show();
        } else {
            self.$el.removeClass('oe_form_readonly').addClass('oe_form_editable');
            self.$buttons.find('.oe_form_buttons_edit').show();
            self.$buttons.find('.oe_form_buttons_view').hide();
            self.$sidebar.hide();
            this.autofocus();
        }
    },
    autofocus: function() {
        if (this.get("actual_mode") !== "view" && !this.options.disable_autofocus) {
            var fields_order = this.fields_order.slice(0);
            if (this.default_focus_field) {
                fields_order.unshift(this.default_focus_field.name);
            }
            for (var i = 0; i < fields_order.length; i += 1) {
                var field = this.fields[fields_order[i]];
                if (!field.get('effective_invisible') && !field.get('effective_readonly') && field.$label) {
                    if (field.focus() !== false) {
                        break;
                    }
                }
            }
        }
    },
    on_button_save: function() {
        var self = this;
        return this.save().done(function(result) {
            self.trigger("save", result);
            self.reload().then(function() {
                self.to_view_mode();
                var parent = self.ViewManager.ActionManager.getParent();
                if(parent){
                    parent.menu.do_reload_needaction();
                }
            });
        });
    },
    on_button_cancel: function(event) {
        if (this.can_be_discarded()) {
            if (this.get('actual_mode') === 'create') {
                this.trigger('history_back');
            } else {
                this.to_view_mode();
                this.trigger('load_record', this.datarecord);
            }
        }
        this.trigger('on_button_cancel');
        return false;
    },
    on_button_new: function() {
        var self = this;
        this.to_edit_mode();
        return $.when(this.has_been_loaded).then(function() {
            if (self.can_be_discarded()) {
                return self.load_defaults();
            }
        });
    },
    on_button_edit: function() {
        return this.to_edit_mode();
    },
    on_button_create: function() {
        this.dataset.index = null;
        this.do_show();
    },
    on_button_duplicate: function() {
        var self = this;
        return this.has_been_loaded.then(function() {
            return self.dataset.call('copy', [self.datarecord.id, {}, self.dataset.context]).then(function(new_id) {
                self.record_created(new_id);
                self.to_edit_mode();
            });
        });
    },
    on_button_delete: function() {
        var self = this;
        var def = $.Deferred();
        this.has_been_loaded.done(function() {
            if (self.datarecord.id && confirm(_t("Do you really want to delete this record?"))) {
                self.dataset.unlink([self.datarecord.id]).done(function() {
                    if (self.dataset.size()) {
                        self.execute_pager_action('next');
                    } else {
                        self.do_action('history_back');
                    }
                    def.resolve();
                });
            } else {
                $.async_when().done(function () {
                    def.reject();
                })
            }
        });
        return def.promise();
    },
    can_be_discarded: function() {
        if (this.$el.is('.oe_form_dirty')) {
            if (!confirm(_t("Warning, the record has been modified, your changes will be discarded.\n\nAre you sure you want to leave this page ?"))) {
                return false;
            }
            this.$el.removeClass('oe_form_dirty');
        }
        return true;
    },
    /**
     * Triggers saving the form's record. Chooses between creating a new
     * record or saving an existing one depending on whether the record
     * already has an id property.
     *
     * @param {Boolean} [prepend_on_create=false] if ``save`` creates a new
     * record, should that record be inserted at the start of the dataset (by
     * default, records are added at the end)
     */
    save: function(prepend_on_create) {
        var self = this;
        var save_obj = {prepend_on_create: prepend_on_create, ret: null};
        this.save_list.push(save_obj);
        return this._process_operations().then(function() {
            if (save_obj.error)
                return $.Deferred().reject();
            return $.when.apply($, save_obj.ret);
        }).done(function() {
            self.$el.removeClass('oe_form_dirty');
        });
    },
    _process_save: function(save_obj) {
        var self = this;
        var prepend_on_create = save_obj.prepend_on_create;
        try {
            var form_invalid = false,
                values = {},
                first_invalid_field = null,
                readonly_values = {};
            for (var f in self.fields) {
                if (!self.fields.hasOwnProperty(f)) { continue; }
                f = self.fields[f];
                if (!f.is_valid()) {
                    form_invalid = true;
                    if (!first_invalid_field) {
                        first_invalid_field = f;
                    }
                } else if (f.name !== 'id' && (!self.datarecord.id || f._dirty_flag)) {
                    // Special case 'id' field, do not save this field
                    // on 'create' : save all non readonly fields
                    // on 'edit' : save non readonly modified fields
                    if (!f.get("readonly")) {
                        values[f.name] = f.get_value();
                    } else {
                        readonly_values[f.name] = f.get_value();
                    }
                }
            }
            if (form_invalid) {
                self.set({'display_invalid_fields': true});
                first_invalid_field.focus();
                self.on_invalid();
                return $.Deferred().reject();
            } else {
                self.set({'display_invalid_fields': false});
                var save_deferral;
                if (!self.datarecord.id) {
                    // Creation save
                    save_deferral = self.dataset.create(values, {readonly_fields: readonly_values}).then(function(r) {
                        return self.record_created(r, prepend_on_create);
                    }, null);
                } else if (_.isEmpty(values)) {
                    // Not dirty, noop save
                    save_deferral = $.Deferred().resolve({}).promise();
                } else {
                    // Write save
                    save_deferral = self.dataset.write(self.datarecord.id, values, {readonly_fields: readonly_values}).then(function(r) {
                        return self.record_saved(r);
                    }, null);
                }
                return save_deferral;
            }
        } catch (e) {
            console.error(e);
            return $.Deferred().reject();
        }
    },
    on_invalid: function() {
        var warnings = _(this.fields).chain()
            .filter(function (f) { return !f.is_valid(); })
            .map(function (f) {
                return _.str.sprintf('<li>%s</li>',
                    _.escape(f.string));
            }).value();
        warnings.unshift('<ul>');
        warnings.push('</ul>');
        this.do_warn(_t("The following fields are invalid:"), warnings.join(''));
    },
    /**
     * Reload the form after saving
     *
     * @param {Object} r result of the write function.
     */
    record_saved: function(r) {
        this.trigger('record_saved', r);
        if (!r) {
            // should not happen in the server, but may happen for internal purpose
            return $.Deferred().reject();
        }
        return r;
    },
    /**
     * Updates the form' dataset to contain the new record:
     *
     * * Adds the newly created record to the current dataset (at the end by
     *   default)
     * * Selects that record (sets the dataset's index to point to the new
     *   record's id).
     * * Updates the pager and sidebar displays
     *
     * @param {Object} r
     * @param {Boolean} [prepend_on_create=false] adds the newly created record
     * at the beginning of the dataset instead of the end
     */
    record_created: function(r, prepend_on_create) {
        var self = this;
        if (!r) {
            // should not happen in the server, but may happen for internal purpose
            this.trigger('record_created', r);
            return $.Deferred().reject();
        } else {
            this.datarecord.id = r;
            if (!prepend_on_create) {
                this.dataset.alter_ids(this.dataset.ids.concat([this.datarecord.id]));
                this.dataset.index = this.dataset.ids.length - 1;
            } else {
                this.dataset.alter_ids([this.datarecord.id].concat(this.dataset.ids));
                this.dataset.index = 0;
            }
            this.do_update_pager();
            if (this.sidebar) {
                this.sidebar.do_attachement_update(this.dataset, this.datarecord.id);
            }
            //openerp.log("The record has been created with id #" + this.datarecord.id);
            return $.when(this.reload()).then(function () {
                self.trigger('record_created', r);
                return _.extend(r, {created: true});
            });
        }
    },
    on_action: function (action) {
        console.debug('Executing action', action);
    },
    reload: function() {
        var self = this;
        return this.reload_mutex.exec(function() {
            if (self.dataset.index == null) {
                self.trigger("previous_view");
                return $.Deferred().reject().promise();
            }
            if (self.dataset.index == null || self.dataset.index < 0) {
                return $.when(self.on_button_new());
            } else {
                var fields = _.keys(self.fields_view.fields);
                fields.push('display_name');
                return self.dataset.read_index(fields,
                    {
                        context: {
                            'bin_size': true,
                            'future_display_name': true
                        }
                    }).then(function(r) {
                        self.trigger('load_record', r);
                    });
            }
        });
    },
    get_widgets: function() {
        return _.filter(this.getChildren(), function(obj) {
            return obj instanceof instance.web.form.FormWidget;
        });
    },
    get_fields_values: function() {
        var values = {};
        var ids = this.get_selected_ids();
        values["id"] = ids.length > 0 ? ids[0] : false;
        _.each(this.fields, function(value_, key) {
            values[key] = value_.get_value();
        });
        return values;
    },
    get_selected_ids: function() {
        var id = this.dataset.ids[this.dataset.index];
        return id ? [id] : [];
    },
    recursive_save: function() {
        var self = this;
        return $.when(this.save()).then(function(res) {
            if (self.dataset.parent_view)
                return self.dataset.parent_view.recursive_save();
        });
    },
    recursive_reload: function() {
        var self = this;
        var pre = $.when();
        if (self.dataset.parent_view)
                pre = self.dataset.parent_view.recursive_reload();
        return pre.then(function() {
            return self.reload();
        });
    },
    is_dirty: function() {
        return _.any(this.fields, function (value_) {
            return value_._dirty_flag;
        });
    },
    is_interactible_record: function() {
        var id = this.datarecord.id;
        if (!id) {
            if (this.options.not_interactible_on_create)
                return false;
        } else if (typeof(id) === "string") {
            if(instance.web.BufferedDataSet.virtual_id_regex.test(id))
                return false;
        }
        return true;
    },
    sidebar_eval_context: function () {
        return $.when(this.build_eval_context());
    },
    open_defaults_dialog: function () {
        var self = this;
        var display = function (field, value) {
            if (field instanceof instance.web.form.FieldSelection) {
                return _(field.values).find(function (option) {
                    return option[0] === value;
                })[1];
            } else if (field instanceof instance.web.form.FieldMany2One) {
                return field.get_displayed();
            }
            return value;
        }
        var fields = _.chain(this.fields)
            .map(function (field) {
                var value = field.get_value();
                // ignore fields which are empty, invisible, readonly, o2m
                // or m2m
                if (!value
                        || field.get('invisible')
                        || field.get("readonly")
                        || field.field.type === 'one2many'
                        || field.field.type === 'many2many'
                        || field.field.type === 'binary'
                        || field.password) {
                    return false;
                }

                return {
                    name: field.name,
                    string: field.string,
                    value: value,
                    displayed: display(field, value),
                }
            })
            .compact()
            .sortBy(function (field) { return field.string; })
            .value();
        var conditions = _.chain(self.fields)
            .filter(function (field) { return field.field.change_default; })
            .map(function (field) {
                var value = field.get_value();
                return {
                    name: field.name,
                    string: field.string,
                    value: value,
                    displayed: display(field, value),
                }
            })
            .value();

        var d = new instance.web.Dialog(this, {
            title: _t("Set Default"),
            args: {
                fields: fields,
                conditions: conditions
            },
            buttons: [
                {text: _t("Close"), click: function () { d.close(); }},
                {text: _t("Save default"), click: function () {
                    var $defaults = d.$el.find('#formview_default_fields');
                    var field_to_set = $defaults.val();
                    if (!field_to_set) {
                        $defaults.parent().addClass('oe_form_invalid');
                        return;
                    }
                    var condition = d.$el.find('#formview_default_conditions').val(),
                        all_users = d.$el.find('#formview_default_all').is(':checked');
                    new instance.web.DataSet(self, 'ir.values').call(
                        'set_default', [
                            self.dataset.model,
                            field_to_set,
                            self.fields[field_to_set].get_value(),
                            all_users,
                            true,
                            condition || false
                    ]).done(function () { d.close(); });
                }}
            ]
        });
        d.template = 'FormView.set_default';
        d.open();
    },
    register_field: function(field, name) {
        this.fields[name] = field;
        this.fields_order.push(name);
        if (JSON.parse(field.node.attrs.default_focus || "0")) {
            this.default_focus_field = field;
        }

        field.on('focused', null, this.proxy('widgetFocused'))
             .on('blurred', null, this.proxy('widgetBlurred'));
        if (this.get_field_desc(name).translate) {
            this.translatable_fields.push(field);
        }
        field.on('changed_value', this, function() {
            if (field.is_syntax_valid()) {
                this.trigger('field_changed:' + name);
            }
            if (field._inhibit_on_change_flag) {
                return;
            }
            field._dirty_flag = true;
            if (field.is_syntax_valid()) {
                this.do_onchange(field);
                this.on_form_changed(true);
                this.do_notify_change();
            }
        });
    },
    get_field_desc: function(field_name) {
        return this.fields_view.fields[field_name];
    },
    get_field_value: function(field_name) {
        return this.fields[field_name].get_value();
    },
    compute_domain: function(expression) {
        return instance.web.form.compute_domain(expression, this.fields);
    },
    _build_view_fields_values: function() {
        var a_dataset = this.dataset;
        var fields_values = this.get_fields_values();
        var active_id = a_dataset.ids[a_dataset.index];
        _.extend(fields_values, {
            active_id: active_id || false,
            active_ids: active_id ? [active_id] : [],
            active_model: a_dataset.model,
            parent: {}
        });
        if (a_dataset.parent_view) {
            fields_values.parent = a_dataset.parent_view.get_fields_values();
        }
        return fields_values;
    },
    build_eval_context: function() {
        var a_dataset = this.dataset;
        return new instance.web.CompoundContext(a_dataset.get_context(), this._build_view_fields_values());
    },
});

};

// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax:
