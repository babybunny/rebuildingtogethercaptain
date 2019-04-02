define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, RoomFormView, template) {
        var fields = [{
                name: "position_name",
                label: "Position name",
                control: "input",
                type: "text",
                required: true
            },{
                name: "hourly_rates.form_rad.attributes.rate",
                label: "Hourly Rate",
                control: "input",
                type: "text",
            },{
                name: "hourly_rates.form_rad.attributes.date",
                label: "Hourly Date",
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHighlight: true, format: "yyyy-mm-dd"},
            },{
                name: "mileage_rates.form_rad.attributes.rate",
                label: "Mileage Rate",
                control: "input",
                type: "text"
            },{
                name: "mileage_rates.form_rad.attributes.date",
                label: "Mileage Date",
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHighlight: true, format: "yyyy-mm-dd"},
            },{
                name: "submit",
                control: "button",
                extraClasses: ['btn-primary'],
                label: "Save changes"
            }
        ];
        var ViewFactory = function(app, loading) {
            return new RoomFormView({
                name: 'staffposition',
                    template: template,
                    model: app.models.staffposition,
                    loading: loading,
                    fields: fields,
                    events: {
                        'click button[name=submit]': function(){
                            this.model.get('hourly_rates').add_form_rad();
                            this.model.get('mileage_rates').add_form_rad();
                        }
                    }
            });
        }
        return ViewFactory;
    }
)
