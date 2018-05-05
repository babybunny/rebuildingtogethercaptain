define([
    'bootstrap-datepicker',
    'app/views/rooms_form',
    'text!app/templates/simple_form.html'],

    function(datepicker,  RoomFormView, template) {
        datepicker = $.fn.datepicker.defaults;
        datepicker.format= "yyyy-mm-dd";
        datepicker.assumeNearbyYear = true;
        datepicker.todayHighlight= true;
        datepicker.todayBtn= true;
        datepicker.autoclose= true;

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
                required: true
            },
            {   control: "spacer"   },
            {
                name: "hourly_rate",
                label: "Hourly rate",
                control: "input"
            },
            {
                name: "hourly_start_date",
                label: "Hourly start date",
                control: "datepicker",
                placeholder: "yyyy-mm-dd",
                helpMessage: "Modified hourly rate will be adjusted on this date."
            },
            {   control: "spacer"   },
            {
                name: "mileage_rate",
                label: "Mileage rate",
                control: "input"
            },
            {
                name: "mileage_start_date",
                label: "Mileage start date",
                control: "datepicker",
                placeholder: "yyyy-mm-dd",
                helpMessage: "Modified mileage rate will be adjusted on this date"
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
