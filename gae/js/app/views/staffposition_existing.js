define(
    [
        'backbone', 'backform', 'bootstrap','bootstrap-datepicker',
        'app/models/rate_after_date', 'text!app/templates/staffposition.html'
    ],
    function(Backbone, Backform, bootstrap, bsdp,
              RateAfterDate, template) {

        var labels = {
            rates: {
                hourly_rates: 'Hourly Rate',
                mileage_rates: 'Mileage Rate'},
            'dates': {
                hourly_rates: 'Hourly Date',
                mileage_rates: 'Mileage Date'},

        };
        var fields = [
            {
                name: "rate",
                control: "input",
                updateLabel: function(type){
                    return labels.rates[type];
                }
            },
            {
                name: "date",
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHighlight: true, format: "yyyy-mm-dd"},
                updateLabel: function(type){
                    return labels.dates[type];
                }
            },
            {
                control: "button",
                extraClasses: ['btn-primary', 'btn-sm'],
                name: "addRate",
                label: "Save"
            }
        ];
        var View = Backbone.View.extend({
            el: '#simple-form-view',
            events: {
                'click td.remove': 'removeRate',
                'click button[name=addRate]': 'addRate',
                'click button[name=saveExit]': 'saveExit',
                'click td.edit': 'editRate',
                'click th.new-rad': 'newRate',
                'click span.new-rad': 'newRate',
            },
            initialize: function(options) {
                var self = this;
                this.options = options;
                self.staffposition = options.staffposition;
                self.basicFields = options.basicFields;
                self.template = _.template(options.template);
                self.loading = options.loading;

                 this.listenTo(this.staffposition, 'change',
                    function(staffposition){
                        if (self.loading){
                            self.loading = false;
                            self.hourly_rates = self.staffposition.get('hourly_rates');
                            self.mileage_rates = self.staffposition.get('mileage_rates');
                            self.makeForm(this.staffposition, this.basicFields).render();
                        }
                    });
            },
            makeForm: function(mdl, fields){
                this.form =  new Backform.Form({
                    model: mdl,
                    fields: fields,
                    showRequiredAsAsterisk: true,
                });
                this.firstfield = this.getFirstField();
                this.form.setElement('#form');
                return this;
            },
            renderForm: function(type){
                if (type){
                    _.each(this.form.fields.models, function(model) {
                        if(model.has('updateLabel')){
                            model.set('label', model.get('updateLabel')(type));
                       }
                    }
                );
                }
                this.form.setElement('#form').render();
                this.form.$el.find('label.control-label:contains("*")').addClass('required');
                this.form.$el.find(this.firstfield).focus();
            },
            render: function(type) {
                if (!this.loading){
                    this.$el.html(this.template({
                        hourly_rates:this.hourly_rates.models,
                        mileage_rates: this.mileage_rates.models
                    }));
                    this.renderForm(type);
                }
            },
            getFirstField: function() {
                var field_list = _.reject(
                    this.form.fields.models,
                    function(model) { return model.get('disabled'); }
                );
                return "[name="+field_list[0].get('name')+"]";
            },
            newRate: function(e){
                var type = e.target.attributes.rt.value;
                this.makeForm(new RateAfterDate(), fields);
                this.form.type = e.target.attributes.rt.value;
                this.render(type);
            },
            fadeRow:function(e){
                this.$('tr').removeClass('fade');
                this.$(e.target).parents('tr').addClass('fade');
                return;
            },
            editRate: function(e){
                this.fadeRow(e);
                var type = e.target.attributes.rt.value;
                this.makeForm(this[type].get(e.target.id), fields);
                this.form.type = type;
                this.form.editing = e.target.id;
                this.renderForm(type);
            },
            removeRate: function(e) {
                var type = e.target.attributes.rt.value;
                this[type].remove(e.target.id);
                this.saveContinue();
            },
            addRate: function(e){
                e.preventDefault();
                this.form.model.validate_protorpc();
                if (this.form.model.isValid()) {
                    var type = this.form.type;
                    this[type].remove(this.form.model.editing);
                    this[type].add(this.form.model);
                    this.saveContinue();
                } else {
                    this.displayError(this.form.model.validationError);
                }
            },
            displayError: function(msg){
                $('div.form-group.has-error > div > span').css('color', 'red');
                $('span.status').css('color', 'red').html(msg).show();
            },
            returnSuccess: function(msg, exit){
                if (exit){
                    console.log(exit)
                    $('span.status').css('color', '#409b27').html(msg).show()
                        .fadeOut({ duration: 1000,
                            complete: function() {
                                window.location = $('#rooms-form-after-save').attr('href');
                            }
                        });
                } else {
                    this.makeForm(this.staffposition, this.basicFields).render();
                }
            },
            saveStaffPosition: function(exit){
                var self = this;
                this.staffposition.save(null,
                    {'success': function(model, attrs, response) {
                        self.returnSuccess('Saved!', exit);
                    },
                    'error': function(model, response, error) {
                        self.displayError(response.responseText);
                    },
                });
            },
            saveExit: function(e) {
                e.preventDefault();
                this.staffposition.set({
                    'position_name': this.form.model.get('position_name'),
                    'hourly_rates': this.hourly_rates,
                    'mileage_rates': this.mileage_rates
                });
                this.saveStaffPosition(true);
            },
            saveContinue: function(){
                this.staffposition.set({
                    hourly_rates: this.hourly_rates,
                    mileage_rates: this.mileage_rates
                });
                this.saveStaffPosition();
            }
        });
        return View;
    }
);
