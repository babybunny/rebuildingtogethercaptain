define(
    [
        'backbone', 'backform', 'bootstrap','bootstrap-datepicker',
        'app/models/rate_after_date', 'text!app/templates/staffposition.html'
    ],
    function(Backbone, Backform, bootstrap, bsdp,
              StaffPositionRateAfterDate, template) {
        var fields = [
            {
                name: "position_name",
                label: "Position Name",
                control: "input",
                required: true
            },
            {
                name: "rate",
                label: "New Rate",
                control: "input",
                updateLabel: function(){
                    return 'Edit Rate';
                }
            },
            {
                name: "date",
                label: "New Date",
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHighlight: true, format: "yyyy-mm-dd"},
                updateLabel: function(){
                    return 'Edit Date';
                }
            },
            {
                name: "type",
                control: "select",
                options: [
                    {label: "--- select Rate Type---", value: ""},
                    {label: "Hourly", value: "hourly_rates"},
                    {label: "Mileage", value: "mileage_rates"},
                ],
                changeDisabled: true
            },
            {
                control: "button",
                extraClasses: ['btn-primary', 'btn-sm'],
                name: "saveChanges",
                label: "Save changes"
            }
        ];
        var View = Backbone.View.extend({
            el: '#simple-form-view',
            events: {
                'click td.remove': 'removeRate',
                'click button[name=saveChanges]': 'saveStep1',
                'click td.edit': 'editRate'
            },
            initialize: function(app, id) {
                var self = this;
                this.app = app;

                this.staffposition = self.app.models.staffposition;
                this.staffposition.fetch().then(function(mdl) {
                        self.hourly_rates = mdl.hourly_rates;
                        self.mileage_rates = mdl.mileage_rates;
                        self.template = _.template(template);
                        self.model = new StaffPositionRateAfterDate({position_name: mdl.position_name});
                        self.loaded = true;
                        self.makeForm().render();
                    });
            },
            saveStep1: function(e) {
                e.preventDefault();
                this.model.validate_protorpc();
                if (this.model.isValid()){
                    var type = this.model.get('type');
                    if (type){
                        this[type].remove(this.model.editing);
                        this[type].add(this.model);
                    }
                    this.saveStep2();
                 }else{
                    $('div.form-group.has-error > div > span').css('color', 'red');
                    $('div.form-group.saveChanges > div > span.status')
                        .css('color', 'red')
                        .text(this.model.validationError)
                        .show();
                }
            },
            editRate: function(e){
                var type = e.target.attributes.rt.value;
                var mdl = this[type].get(e.target.id);
                this.model.editing = e.target.id;
                this.model.set({
                    type: type,
                    rate: mdl.get('rate'),
                    date: mdl.get('date')
                });
                this.$(e.target).parents('tr').addClass('fade');
                this.updateFormLabels().render_form();
            },
            getFirstField: function() {
                var field_list = _.reject(
                    this.form.fields.models,
                    function(model) { return model.get('disabled'); }
                );
                return field_list[0]._previousAttributes;
            },
             updateFormLabels: function() {
                 _.each(this.form.fields.models, function(model) {
                        if(model.has('updateLabel')){
                            model.set('label', model.get('updateLabel')());
                       }
                       else if(model.has('changeDisabled')){
                            model.set('disabled', true);
                       }
                    }
                );
                 return this;
            },
            makeForm: function() {
                this.form = new Backform.Form({
                    model: this.model,
                    fields: fields,
                    showRequiredAsAsterisk: true,
                });
                return this;
            },
            removeRate: function(e) {
                var type = e.target.attributes.rt.value;
                this[type].remove(e.target.id);
                this.saveStep2();
            },
            render: function() {
                if (this.loaded){
                    this.$el.html(this.template({
                        hourly_rates:this.hourly_rates.models,
                        mileage_rates: this.mileage_rates.models
                    }));
                }
                this.render_form();
            },
            render_form: function(){
                if (this.form){
                    this.firstfield = this.getFirstField();
                    this.form.setElement('#rate-form').render();
                    this.$el.find('label.control-label:contains("*")').addClass('required');
                    this.$el.find('[name=' + this.firstfield.name +']').focus();
                }
            },
            saveStep2: function(){
                var self = this;
                this.staffposition.set({
                    position_name: this.model.get('position_name'),
                    hourly_rates: this.hourly_rates,
                    mileage_rates: this.mileage_rates
                });
                this.staffposition.save(null,
                    {'success': function(){
                        self.model = new StaffPositionRateAfterDate({position_name: self.staffposition.get('position_name')});
                        self.makeForm().render();
                    },
                    'error': function(model, response, error) {
                        $('div.form-group.saveChanges > div > span.status')
                            .css('color', 'red')
                            .text('Error: ' + response.responseText)
                            .show();
                        },
                    });
            },
        });
        return View;
    }
);
