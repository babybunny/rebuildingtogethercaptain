define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, RoomFormView, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
            },
            {
                name: "name",
                label: "Position name",
                control: "input",
                type: "text",
                required: true
            },
            {
                label: "Hourly (new rate)",
                name: "hourly_rate",
                control: "input",
            },
            {
                name: "hourly_date",
                label: "Hourly (start date)",

                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHiglight: true, format: "yyyy-mm-dd"},
            },
            {
                name: "mileage_rate",
                label: "Mileage (new rate)",
                control: "input"
            },
            {
                name: "mileage_date",
                label: "Mileage (start date)",
                control: "datepicker",
                options: {autoclose: true, assumeNearbyYear: true, todayHiglight: true, format: "yyyy-mm-dd"},
            },
            {
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
                    fields: fields,
            });
        }
        return ViewFactory;
    }
)
