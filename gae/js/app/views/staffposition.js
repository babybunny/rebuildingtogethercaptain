define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
        'text!app/templates/simple_form.html',
        'app/models/rate_after_date'
    ],
    function(bsdp, RoomFormView, template, RateAfterDate) {
        var fields = [{
                name: "position_name",
                label: "Position name",
                control: "input",
                type: "text",
                required: true
            },{
                name: "hourly_rate",
                label: "Hourly Rate",
                control: "input",
                type: "text",
            },{
                name: "hourly_date",
                label: "Hourly Date",
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHighlight: true, format: "yyyy-mm-dd"},
            },{
                name: "mileage_rate",
                label: "Mileage Rate",
                control: "input",
                type: "text"
            },{
                name: "mileage_date",
                label: "Mileage Date",
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHighlight: true, format: "yyyy-mm-dd"},
            },{
                id: "submit",
                control: "button",
                extraClasses: ['btn-primary'],
                label: "Save changes"
            }
        ];
        var ViewFactory = function(app, loading) {
            var hrad = new RateAfterDate(app, 'hourly_');
            var mrad = new RateAfterDate(app, 'mileage_');

            return new RoomFormView({
                name: 'staffposition',
                    template: template,
                    model: app.models.staffposition,
                    loading: loading,
                    fields: fields,
                    events: {
                        'click button': function(e){
                            this.model.trigger('submit', this.model);
                        }
                    }
            });
        }
        return ViewFactory;
    }
)
