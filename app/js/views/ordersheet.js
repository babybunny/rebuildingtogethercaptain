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
            {
                name: "name",
                label: "Name",
                control: "input",
            },
            {
                name: "visibility",
                label: "Visibility",
                control: "select",
                options: [
                    {label: "Everyone", value: "Everyone"},
                    {label: "Staff Only", value: "Staff Only"},
                ]
            },
            {
                name: "supports_extra_name_on_order",
                label: "Supports extra name on order",
		            control: "checkbox"
            },
            {
                name: "code",
                label: "Code",
                control: "input",
                helpMessage: "Three-letter code like LUM for Lumber"
            },
            {
                name: "instructions",
                label: "Instructions",
                control: "textarea",
                helpMessage: "Instructions to Captain, appears on order form"
            },
            {
                name: "logistics_instructions",
                label: "Logistics instructions",
                control: "textarea",
                helpMessage: "Instructions to Captain, appears on logistics form"
            },
            {
                name: "default_supplier",
                label: "Default supplier",
                    control: ModelSelectControl,
                    room_model_module: SupplierChoices,
                helpMessage: "Default Supplier, used if Item's supplier is not set."
            },
            {
                name: "delivery_options",
                label: "Delivery options",
                control: "select",
                options: [
                    {label: "No", value: "No"},
                    {label: "Yes", value: "Yes"},
                ],
                helpMessage: "Allow Captain to select Delivery to site"
            },
            {
                name: "pickup_options",
                label: "Pick-up options",
                control: "select",
                options: [
                    {label: "No", value: "No"},
                    {label: "Yes", value: "Yes"},
                ],
                helpMessage: "Allow Captain to select Pick-up from RTP warehouse"
            },
            {
                name: "retrieval_options",
                label: "Retrieval options",
                control: "select",
                options: [
                    {label: "No", value: "No"},
                    {label: "Yes", value: "Yes"},
                ],
                helpMessage: "Drop-off and retrieval (like debris box) <span style='display:block'>Note: do not set this with either <i>Delivery or Pick-up</i>.</span>",
            },
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
