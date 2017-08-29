define(
    [
        'app/views/rooms_form',
        'text!app/templates/simple_form.html'
    ],
    function(RoomFormView, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
            },
            {
                name: "rooms_id",
                label: "Rooms id",
                control: "input",
            },
            {
                name: "name",
                label: "Name",
                control: "input",
                required: true
            },
            {
                name: "email",
                label: "Email",
                control: "input",
                type: "email"
            },
            {
                name: "tshirt_size",
                label: "Tshirt size",
                control: "select",
                options: [
                    {label: '--- please select one ---', value: null},
                    {label: "Small", value: "Small"},
                    {label: "Medium", value: "Medium"},
                    {label: "Large", value: "Large"},
                    {label: "X-Large", value: "X-Large"},
                    {label: "2XL", value: "2XL"},
                    {label: "3XL", value: "3XL"},
                ]
            },
            {
                name: "phone_mobile",
                label: "Phone mobile",
                control: "input",
            },
            {
                name: "phone_work",
                label: "Phone work",
                control: "input",
            },
            {
                name: "phone_home",
                label: "Phone home",
                control: "input",
            },
            {
                name: "phone_fax",
                label: "Phone fax",
                control: "input",
            },
            {
                name: "phone_other",
                label: "Phone other",
                control: "input",
            },
            {
                name: "notes",
                label: "Notes",
                control: "textarea",
            },
            {
                id: "submit",
                control: "button",
                label: "Save changes"
            }
        ];

        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'captain',
		            template: template,
		            model: app.models.captain,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
