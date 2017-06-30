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
            },
            {
                name: "delivery_options",
                label: "Delivery options",
                control: "select",
		            default: "No",
                options: [
                    {label: "Yes", value: "Yes"},
                    {label: "No", value: "No"},
                ],
            },
            {
                name: "retrieval_options",
                label: "Retrieval options",
                control: "select",
		            default: "No",
                options: [
                    {label: "Yes", value: "Yes"},
                    {label: "No", value: "No"},
                ]
            },
            /* TODO     {
               name: "supports_extra_name_on_order",
               label: "Supports extra name on order",
               // "supports_extra_name_on_order is a BooleanProperty('supports_extra_name_on_order', default=False).  TODO",
               },
            */
            {
                name: "pickup_options",
                label: "Pickup options",
                control: "select",
		            default: "No",
                options: [
                    {label: "Yes", value: "Yes"},
                    {label: "No", value: "No"},
                ]
            },
            {
                name: "default_supplier",
                label: "Defaultsupplier",
                control: ModelSelectControl,
		            room_model_module: SupplierChoices,
            },
            {
                name: "instructions",
                label: "Instructions",
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
