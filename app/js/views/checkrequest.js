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
                    {label: "submitted", value: "submitted"},
                    {label: "payable", value: "payable"},
                ]
            },
            {
                name: "captain",
                label: "Captain",
		            control: ModelSelectControl,
		            room_model_module: CaptainChoices,
            },
            {
                name: "payment_date",
                label: "Payment date",
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
		            required: true
            },
            {
                name: "name",
                label: "Name",
                control: "input",
		            required: true
            },
            {
                name: "address",
                label: "Address",
                control: "textarea",
            },
            {
                name: "tax_id",
                label: "Tax id",
                control: "input",
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
                ]
            },
            {
                name: "materials_amount",
                label: "Materials amount",
                control: "input",
            },
            {
                name: "labor_amount",
                label: "Labor amount",
                control: "input",
            },
            {
                name: "food_amount",
                label: "Food amount",
                control: "input",
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
