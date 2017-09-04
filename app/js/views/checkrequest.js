define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
	    'app/views/model_select_control',
        'app/models/captain_choices',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, RoomFormView, ModelSelectControl, CaptainChoices, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
            },
            {
                name: "site",
                label: "Site",
                control: "input",
                disabled: true
            },
            {
                name: "program",
                label: "Program",
                control: "input",
                type: "text"
            },
            {
                name: "captain",
                label: "Captain",
                    control: ModelSelectControl,
                    room_model_module: CaptainChoices
            },
            {
                name: "name",
                label: "Name",
                control: "input",
                required: true,
                helpMessage: "Payable To"
            },
            {
                name: "payment_date",
                label: "Payment date",
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
		           required: true
            },
            {
                name: "labor_amount",
                label: "Labor amount",
                control: "input",
                helpMessage: "Labor Amount ($)"
            },
            {
                name: "materials_amount",
                label: "Materials amount",
                control: "input",
                helpMessage: "Materials Amount ($)"
            },
            {
                name: "food_amount",
                label: "Food amount",
                control: "input",
                helpMessage: "Food Amount ($)"
            },
            {
                name: "description",
                label: "Description",
                control: "textarea"
            },

            {
                name: "address",
                label: "Address",
                control: "textarea",
                helpMessage: "Payee Address"
            },
            {
                name: "tax_id",
                label: "Tax id",
                control: "input",
                helpMessage: "Payee Tax ID, we'll notify you if we still need this information to process the check"
            },
            {
                name: "form_of_business",
                label: "Form of business",
                control: "select",
                options: [
                    {label: "Corporation", value: "Corporation"},
                    {label: "Sole Proprietor", value: "Sole Proprietor"},
                    {label: "Partnership", value: "Partnership"},
                    {label: "Don't Know", value: "Don't Know"},
                ],
                    helpMessage: "Payee Business Type"
            },
            {
                name: "state",
                label: "State",
                control: "select",
                options: [
                    {label: "new", value: "new"},
                    {label: "submitted", value: "submitted"},
                    {label: "payable", value: "payable"},
                    {label: "fulfilled", value: "fulfilled"},
                    {label: "deleted", value: "deleted"}
                ]
            },
            {
                id: "submit",
                control: "button",
                label: "Save changes"
            },

        ];

        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'checkrequest',
		            template: template,
		            model: app.models.checkrequest,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
