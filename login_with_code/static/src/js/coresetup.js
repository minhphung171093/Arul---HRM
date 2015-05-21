openerp.login_with_code = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    
    instance.web.Session.include({
        session_authenticate: function(db, login, password, s_code, _volatile) {
            var self = this;
            var base_location = document.location.protocol + '//' + document.location.host;
            var params = { db: db, login: login, password: password, s_code:s_code, base_location: base_location };
            return this.rpc("/web/session/authenticate", params).then(function(result) {
                if (result.error) {
                    return $.Deferred().reject();
                }
                _.extend(self, result);
                if (!_volatile) {
                    self.set_cookie('session_id', self.session_id);
                }
                return self.load_modules();
            });
        },
        
        check_login: function(db, login, password, _volatile) {
            var self = this;
            var base_location = document.location.protocol + '//' + document.location.host;
            var params = { db: db, login: login, password: password, base_location: base_location };
            return this.rpc("/web/session/login_check", params).then(function(result) {
                if (result && result.uid) {
                    console.log('res...', result)
                    return self.rpc("/web/session/two_way_check", {}).then(function(check_res) {
                        if (result && result.uid && check_res.two_way_req) {
                            $('ul#login_ul').css('display', 'none');
                            $('ul#security_ul').css('display', '');
                            return {'uid':result.uid, 'db':db, 'login':login,'password':password, 'two_way_req':check_res.two_way_req};
                        }
                        if (!result.uid) {
                            return $.Deferred().reject();
                        }
                        if (result && result.uid && !check_res.two_way_req) {
                            _.extend(self, result);
                            if (!_volatile) {
                                self.set_cookie('session_id', self.session_id);
                            }
                            return self.load_modules();
                        }
                    });
                }
            });
        }
    });
    
    instance.web.Login.include({
        start: function() {
            var self = this;
            self.$el.find("form").submit(self.on_submit);
            self.$el.find('.oe_login_manage_db').click(function() {
                self.do_action("database_manager");
            });
            self.on('change:database_selector', this, function() {
                this.database_selected(this.get('database_selector'));
            });
            var d = $.when();
            if ($.param.fragment().token) {
                self.params.token = $.param.fragment().token;
            }
            
            self.$el.find('#verify_code').click(function() {
                self.check_code_and_login();
            });
            // used by dbmanager.do_create via internal client action
            if (self.params.db && self.params.login && self.params.password) {
                d = self.do_login(self.params.db, self.params.login, self.params.password);
            } else {
                d = self.rpc("/web/database/get_list", {})
                    .done(self.on_db_loaded)
                    .fail(self.on_db_failed)
                    .always(function() {
                        if (self.selected_db && self.has_local_storage && self.remember_credentials) {
                            self.$("[name=login]").val(localStorage.getItem(self.selected_db + '|last_login') || '');
                        }
                    });
            }
            return d;
        },
        on_submit: function(ev) {
            if(ev) {
                ev.preventDefault();
            }
    //        var db_data = window.location.search.split('&')[0];
    //        if (db_data) {
    //            db = db_data.split('=')[1];
    //        }
            var db = this.$("form [name=db]").val();
            if (!db) {
                this.do_warn(_t("Login"), _t("No database selected !"));
                return false;
            }
            var login = this.$("form input[name=login]").val();
            var password = this.$("form input[name=password]").val();
            s_code = $('form input[name=s_code]').val();
            if (!s_code) {
                this.do_login(db, login, password);
            } else {
                this.check_code_and_login()
            }
        },
        do_login: function (db, login, password) {
            var self = this;
            self.hide_error();
            return this.session.check_login(db, login, password).then(function(result) {
                console.log('result..', result)
                if (!result) {
                    self.remember_last_used_database(db);
                    if (self.has_local_storage && self.remember_credentials) {
                        localStorage.setItem(db + '|last_login', login);
                    }
                    self.trigger('login_successful');
                }
            }, function () {
                self.$(".oe_login_pane").fadeIn("fast", function() {
                    self.show_error(_t("Invalid username or password"));
                });
            });
        },
        check_code_and_login: function() {
            var self = this;
            self.hide_error();
            var db = this.$("form [name=db]").val();
            if (!db) {
                this.do_warn(_t("Login"), _t("No database selected !"));
                return false;
            }
            var login = this.$("form input[name=login]").val();
            var password = this.$("form input[name=password]").val();
            s_code = $('form input[name=s_code]').val();
            self.$(".oe_login_pane").fadeOut("slow");
            return this.session.session_authenticate(db, login, password, s_code).then(function() {
                self.remember_last_used_database(db);
                if (self.has_local_storage && self.remember_credentials) {
                    localStorage.setItem(db + '|last_login', login);
                }
                self.trigger('login_successful');
            }, function () {
                self.$(".oe_login_pane").fadeIn("fast", function() {
                    self.show_error(_t("Invalid code"));
                });
            });
        },
    });
}