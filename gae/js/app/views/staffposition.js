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
            {control: "spacer", disabled: true},
            {
                name: "position_name",
                label: "Position name",
                control: "input",
                required: true
            },
            {
                name: "hourly_rate",
                label: "Hourly rate $",
                placeholder: "0.0",
                control: "input",
            },
            {
                name: "hourly_form_date",
                label: "Hourly rate after date",
                control: "datepicker",
                placeholder: "yyyy-mm-dd",
                helpMessage: "Hourly rate (effective after this date)",
                required: true
            },
            {
                name: "mileage_rate",
                label: "Mileage rate $",
                placeholder: "0.0",
                control: "input"
            },
            {
                name: "mileage_form_date",
                label: "Mileage rate after date",
                control: "datepicker",
                placeholder: "yyyy-mm-dd",
                helpMessage: "Mileage rate (effective after this date)",
                required: true
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
