/*global openerp, _, $ */

openerp.web_m2x_options = function(openerp) {

	var MODELS_TO_HIDE = ['crm.lead'];
    // Hide the create and duplicate button on all page views (i.e. read-only form views)
    openerp.web.PageView.include({
        on_loaded: function(data) {
            var self = this;
            var ret = this._super.apply(this, arguments);
            var res_model = this.dataset.model;
            this.$element.find('button.oe_form_button_create').remove();
            this.$element.find('button.oe_form_button_duplicate').remove();
            return ret;
        },
    });

};

