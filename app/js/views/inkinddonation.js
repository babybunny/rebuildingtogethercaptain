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
                name: "id", // The key of the model attribute
                label: "ID", // The label to display next to the control
                control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
                disabled: true // By default controls are editable. Here we disabled it.
            },
            // boilerplate
            {
                name: "site",
                label: "Site",
                control: "input",
		disabled: true
            },
            {
                name: "state",
                label: "State",
                control: "select",
                options: [
                    {label: "fulfilled", value: "fulfilled"},
                    {label: "new", value: "new"},
                    {label: "deleted", value: "deleted"},
                    {label: "pending letter", value: "pending letter"},
                    {label: "submitted", value: "submitted"},
                ]
            },
            {
                name: "captain",
                label: "Captain",
		control: ModelSelectControl,
		room_model_module: CaptainChoices,
            },
            {
                name: "donation_date",
                label: "Donation date",
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
            },
            {
                name: "donor",
                label: "Donor",
                control: "input",
            },
            {
                name: "donor_phone",
                label: "Donor phone",
                control: "input",
            },
            {
                name: "donor_info",
                label: "Donor info",
                control: "textarea",
            },
            {
                name: "labor_amount",
                label: "Labor amount",
                control: "input",
            },
            {
                name: "materials_amount",
                label: "Materials amount",
                control: "input",
            },
            {
                name: "budget",
                label: "Budget",
                control: "select",
                options: [
                    {label: "Roofing", value: "Roofing"},
                    {label: "Normal", value: "Normal"},
                ],
		default: "Normal"
		
            },
            {
                name: "description",
                label: "Description",
                control: "textarea",
            },
            {
                control: "button",
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
