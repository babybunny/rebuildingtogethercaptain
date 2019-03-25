define(
    [
        'backbone', 'backform', 'bootstrap','bootstrap-datepicker',
        'app/models/rate_after_date',
        'text!app/templates/staffposition_rates.html'
    ],
    function(Backbone, Backform, bootstrap, bsdp,
              NewRateAfterDate,
             template) {
        var fields = [
            {
                name: "rate",
                label: "New Rate",
                required: true,
                control: "input",
            },
            {
                id: "datepicker",
                name: "date",
                label: "Start Date",
                required: true,
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHighlight: true, format: "yyyy-mm-dd"},
            },
            {
                name: "type",
                label: "Rate Type",
                control: "select",
                required: true,
                options: [
                    {label: "--- select rate type---", value: ""},
                    {label: "Hourly", value: "hourly_rates"},
                    {label: "Mileage", value: "mileage_rates"},
                ]
            },
            {
                control: "button",
                extraClasses: ['btn-primary', 'btn-sm'],
                name: "addRate",
                label: "Add Rate"
            }
        ];
        var View = Backbone.View.extend({
            el: '#staffposition-form-view',
            events: {
                'click button.remove-hourly-rate': 'removeHourlyRate',
                'click button.remove-mileage-rate': 'removeMileageRate',
                'click button.edit-hourly-rate': 'editHourlyRate',
                'click button.edit-mileage-rate': 'editMileageRate',
                'click button[name=addRate]': 'addRate',
            },
            initialize: function(options) {
                this.options = options;
                this.template = _.template(template);
                this.model = new NewRateAfterDate({id: this.options.staffposition.get('id')});
                this.hourly_rates = this.options.staffposition.get('hourly_rates');
                this.mileage_rates = this.options.staffposition.get('mileage_rates');
                this.makeForm();
            },
            makeForm: function() {
                this.form = new Backform.Form({
                    model: this.model,
                    fields: fields,
                    showRequiredAsAsterisk: true,
                });
            },
            saveRates: function(type){
                var self = this;
                this.options.staffposition.set({
                    hourly_rates: this.hourly_rates,
                    mileage_rates: this.mileage_rates
                });
                this.options.staffposition.save(null,
                    {'success': function(){
                        self.model = new NewRateAfterDate({id: self.options.staffposition.get('id')});
                        self.makeForm();
                        self.render();
                    },
                    'error': function(model, response, error) {
                        $('div.form-group.addRate > div > span.status')
                            .css('color', 'red')
                            .text(msg)
                            .show();
                        },
                    });
            },
            editHourlyRate:function(e){
                var mdl = this.hourly_rates.get(e.target.id);
                this.model.set({
                    type: "hourly_rates",
                    rate: mdl.get('rate'),
                    date: mdl.get('date')
                })
                this.hourly_rates.remove(e.target.id);
                this.render()

            },
            editMileageRate:function(e){
                var mdl = this.mileage_rates.get(e.target.id);
                this.model.set({
                    type: "mileage_rates",
                    rate: mdl.get('rate'),
                    date: mdl.get('date')
                })
                this.mileage_rates.remove(e.target.id);
                this.render()

            },
            removeHourlyRate: function(e) {
                this.hourly_rates.remove(e.target.id);
                this.saveRates();
            },
            removeMileageRate: function(e) {
                this.mileage_rates.remove(e.target.id);
                this.saveRates();
            },
            addRate: function(e) {
                e.preventDefault();
                this.model.validate_protorpc();
                if (this.model.isValid(this.model.attributes)){
                    if (this.model.get('type') == "hourly_rates"){
                        this.hourly_rates.add(this.model);
                    }
                    else if (this.model.get('type') == "mileage_rates"){
                        this.mileage_rates.add(this.model);
                    }
                    this.saveRates();
                }else{
                    $('div.form-group.has-error > div > span').css('color', 'red')
                    $('div.form-group.addRate > div > span.status')
                        .css('color', 'red')
                        .text("Validation errors. Please fix.")
                        .show();
                }
            },
            render: function() {
                this.$el.html(this.template({
                    hourly_rates:this.hourly_rates.models,
                    mileage_rates: this.mileage_rates.models,
                    position_name: this.options.staffposition.get('position_name'),
                }));
                this.form.setElement('#rate-form');
                this.form.render().$el.find('label.control-label:contains("*")').addClass('required');
                return this;
            }
        });
        return View;
    }
);
