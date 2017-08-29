define(
    [
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/supplier_choices',
        'text!app/templates/simple_form.html'
    ],
    function(RoomFormView, ModelSelectControl, SupplierChoices, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
            },
            // boilerplate
            {
                name: "code",
                label: "Code",
                control: "input",
                helpMessage: "Three-letter code like LUM for Lumber"
            },
            {
                name: "name",
                label: "Name",
                control: "input",
            },
            {
                name: "visibility",
                label: "Visibility",
                control: "select",
		            default: "Everyone",
                options: [
                    {label: "Everyone", value: "Everyone"},
                    {label: "Staff Only", value: "Staff Only"},
                ]
            },
            {
                name: "logistics_instructions",
                label: "Logistics instructions",
                control: "textarea",
                default: "",
                helpMessage: "Instructions to Captain, appears on logistics form"
            },
            {
                name: "instructions",
                label: "Instructions",
                control: "textarea",
                default: "",
                helpMessage: "Instructions to Captain, appears on order form"
            },
            {
                name: "default_supplier",
                label: "Default supplier",
                control: ModelSelectControl,
		            room_model_module: SupplierChoices,
                helpMessage: "Default Supplier, used if Item's supplier is not set."
            },
            {
                label: "Default Supplier, used if Item's supplier is not set.",
                control: "help"
            },
            {
                name: "supports_extra_name_on_order",
                label: "Supports extra name on order",
		            control: "checkbox"
            },
            {control: "spacer"},
            {
                label: "Choose one of the next three options.",
                control: "help"
            },
            {
                name: "delivery_options",
                label: "Delivery options",
                control: "select",
                    default: "No",
                options: [
                    {label: "No", value: "No"},
                    {label: "Yes", value: "Yes"},
                ],
            },
            {
                label: "Allow Captain to select Delivery to site",
                control: "help"
            },
            {
                name: "retrieval_options",
                label: "Retrieval options",
                control: "select",
                    default: "No",
                options: [
                    {label: "No", value: "No"},
                    {label: "Yes", value: "Yes"},
                ],
            },
            {
                label: "Drop-off and retrieval (like debris box) Note: do not set this with either delivery or pick-up",
                control: "help"
            },
            {
                name: "pickup_options",
                label: "Pickup options",
                control: "select",
		            default: "No",
                options: [
                    {label: "No", value: "No"},
                    {label: "Yes", value: "Yes"},
                ],
                // helpMessage: "Allow Captain to select Pick-up from RTP warehouse"
            },
            {
                label: "Allow Captain to select Pick-up from RTP warehouse",
                control: "help"
            },
            {control: "spacer"},
            {
                id: "submit",
                control: "button",
                label: "Save changes"
            }
        ];

        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'ordersheet',
		            template: template,
		            model: app.models.ordersheet,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
