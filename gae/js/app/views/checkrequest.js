define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
	'app/views/model_select_control',
        'app/models/captain_choices',
        'app/models/captain_for_site_choices',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp,
	     RoomFormView,
	     ModelSelectControl,
	     CaptainChoices,
	     CaptainForSiteChoice,
	     template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
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
		room_model_module: CaptainForSiteChoice
            },
            {
                name: "name",
                label: "Name",
                helpMessage: "Payable To",
                control: "input",
                required: true
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
                label: "Labor Amount ($)",
                control: "input"
            },
            {
                name: "materials_amount",
                label: "Materials Amount ($)",
                control: "input"
            },
            {
                name: "food_amount",
                label: "Food Amount ($)",
                control: "input"
            },
            {
                name: "description",
                label: "Description",
                control: "textarea",
                helpMessage: "Please include place of purchase and list of items purchased, and submit corresponding recipt."
            },

            {
                name: "address",
                label: "Address",
                helpMessage: "Payee Address",
                control: "textarea"
            },
            {
                name: "tax_id",
                label: "Tax ID",
                control: "input",
                helpMessage: "Payee Tax ID  (We'll notify you if we still need this information to process the check)"
            },
            {
                name: "form_of_business",
                label: "Form of Business",
                helpMessage: "Payee Business Type",
                control: "select",
                options: [
                    {label: "Corporation", value: "Corporation"},
                    {label: "Sole Proprietor", value: "Sole Proprietor"},
                    {label: "Partnership", value: "Partnership"},
                    {label: "Don't Know", value: "Don't Know"},
                ]
            },
            {
                id: "submit",
                extraClasses: ['btn-primary'],
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
