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
                name: "donation_date",
                label: "Donation date",
                control: "datepicker",
                options: {format: "yyyy-mm-dd"}
            },
            {
                name: "donor",
                label: "Donor",
                control: "input",
                type: "text"
            },
            {
                name: "donor_phone",
                label: "Donor phone",
                control: "input",
                type: "text"
            },
            {
                name: "donor_info",
                label: "Donor info",
                control: "textarea",
                helpMessage: 'Include as much of the following donor information as possible:<br>donor name, company, address, phone, email.'
            },
            {
                name: "labor_amount",
                label: "Labor Value ($)",
                control: "input",
                default: 0.0,
            },
            {
                name: "materials_amount",
                label: "Materials Value ($)",
                control: "input",
                default: 0.0
            },
            {
                name: "description",
                label: "Description",
                control: "textarea"
            },
            {
                name: "budget",
                label: "Budget",
                control: "select",
                options: [
                    {label: "Normal", value: "Normal"},
                    {label: "Roofing", value: "Roofing"}
                ],
		default: "Normal"
            },
            {
                name: "state",
                label: "State",
                control: "select",
                options: [
                    {label: "new", value: "new"},
                    {label: "submitted", value: "submitted"},
                    {label: "pending letter", value: "pending letter"},
                    {label: "fulfilled", value: "fulfilled"},
                    {label: "deleted", value: "deleted"}
                ],
                default: "new"
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
		name: 'inkinddonation',
		template: template,
		model: app.models.inkinddonation,
		loading: loading,
		fields: fields,
	    });
        }
        return ViewFactory;
    }
)
