define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
        'text!app/templates/simple_form.html',
        'app/views/staffposition_existing',
    ],
    function(bsdp, RoomFormView, template, StaffPositionExistingView) {
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

            if (app.models['staffposition'].isNew()) {
                return new RoomFormView({
                    name: 'staffposition',
                        template: template,
                        model: app.models.staffposition,
                        loading: loading,
                        fields: fields
                });
            }
            return new StaffPositionExistingView(app, app.models.staffposition.id);
        }
        return ViewFactory;
    }
)
