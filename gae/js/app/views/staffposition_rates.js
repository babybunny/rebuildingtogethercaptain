define(
    [
        'backbone', 'backform', 'bootstrap','bootstrap-datepicker',
        'text!app/templates/staffposition_rates.html', 'app/models/rate_after_date',
    ],
    function(Backbone, Backform, bootstrap, bsdp, template, RateAfterDate) {
        var fields = [
            {
                name: "rate",
                control: "input",
                updateLabel: function(name){
                    this.label = name + ' Rate';
                }
            },{
                name: "date",
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHighlight: true, format: "yyyy-mm-dd", orientation: 'bottom right'},
                updateLabel: function(name){
                    this.label = name + ' Date';
                }
            },{
                control: "button",
                extraClasses: ['btn-primary', 'btn-sm'],
                name: "updateRates",
                updateBtn: function(name, action){
                    this.label = action + name + ' Rate';
                }
            },
        ];
        var View = Backbone.View.extend({
            el: '#simple-form-view',
            events: {
                'click th.staffposition-btn.new-rad': 'newRate',
                'click td .staffposition-btn.edit': 'editRate',
                'click .staffposition-btn.remove': 'removeRate',
                'click button[name=updateRates]': 'updateRates',
                'click button[name=cancel]': 'render',
            },
            initialize: function(options) {
                var self = this;
                this.options = options;
                this.name = options.name;
                this.templateName = options.templateName;
                this.loading = options.loading;
                this.rates = options.rates;
                this.template = _.template(template);
                this.position_name = 'New Staff Position';
                this.changeTrigger = options.changeTrigger;

                $.fn.modal.Constructor.Default.backdrop = false
                this.modalId = "#".concat(this.name).concat('Modal');

                this.on('finished-loading', function(rates, position_name){
                    this.loading = false;
                    self.rates = rates;
                    self.position_name = position_name;
                    this.render();
                });
            },
            makeForm: function(mdl, action){
                return new Backform.Form({
                    model: mdl,
                    fields: this.updateFields(action),
                    showRequiredAsAsterisk: true,
                });
            },
            updateFields: function(action){
                var self = this;
                return _.map(fields, function(field) {
                    if(field.updateBtn){
                        field.updateBtn(self.templateName, action);
                    } else{
                        field.updateLabel(self.templateName);
                    }
                    return field;
                });
            },
            render: function(){
                if(!this.loading){
                    this.$el.html(this.template({
                        rates: this.rates.models,
                        name: this.name,
                        templateName: this.templateName,
                        position_name: this.position_name,
                    }));
                }
            },
            renderForm: function(){
                if (this.form) {
                    $(this.modalId).modal('show').css('background', '#000000b3');
                    this.form.setElement(this.$el.find('#rates-form')).render();
                    this.form.$el.find('input').first().trigger('focus');
                }
            },
            editRate: function(e){
                var mdl = this.rates.get(e.target.id);
                this.model = new RateAfterDate({
                    rate: mdl.get('rate'),
                    date: mdl.get('date')
                });
                this.form = this.makeForm(this.model, 'Edit ');
                this.form.editId = e.target.id;
                this.renderForm();
                this.$(e.target).parents('tr').addClass('fade');
            },
            newRate: function(){
                this.model = new RateAfterDate();
                this.form = this.makeForm(this.model, 'Create ');
                this.renderForm();
            },
            removeRate: function(e){
                this.rates.remove(e.target.id);
                this.changeTrigger();
            },
            updateRates: function(e){
                $(e.target).prop('disabled', true);
                this.model.validate_protorpc();
                if (this.model.isValid()) {
                    this.rates.remove(this.form.editId);
                    this.rates.add(this.model);
                    this.changeTrigger();
                }else{
                    $(e.target).removeAttr('disabled');
                    this.$('div.form-group.has-error > div').css('color', 'red');
                    this.$('span.status').first().css('color', 'red').html(
                        this.model.validationError).show();
                }
            },
        });
        return View;
    }
)
