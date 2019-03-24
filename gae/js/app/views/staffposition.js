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
                name: "hourly_rates.rate",
                label: "Hourly Rate",
                control: "input",
                type: "text"
            },{
                name: "hourly_rates.date",
                label: "Hourly Date",
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHighlight: true, format: "yyyy-mm-dd"},
            },{
                name: "mileage_rates.rate",
                label: "Mileage Rate",
                control: "input",
                type: "text"
            },{
                name: "mileage_rates.date",
                label: "Mourly Date",
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
            return new RoomFormView({
                name: 'staffposition',
                    template: template,
                    model: app.models.staffposition,
                    loading: loading,
                    fields: fields
            });
        }
        return ViewFactory;
    }
)
