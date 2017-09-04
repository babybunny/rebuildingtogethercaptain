define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/supplier_choices',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, RoomFormView, ModelSelectControl, SupplierChoices, template) {
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
                    disabled: true,
                    required: true
            },
            {
                name: "order_sheet",
                label: "Order sheet",
                control: "input",
                    disabled: true,
                    required: true
            },
            {
                name: "program",
                label: "Program",
                control: "input",
                    type: "text"
            },
            {
                name: "sub_total",
                label: "Subtotal",
                control: "input"
                    // float
            },
            {
                name: "state",
                label: "State",
                control: "input",
                    type: "text"
            },
            {
                name: "actual_total",
                label: "Actual total",
                control: "input",
                    // float
                    helpMessage: "Use this is in the rare case when the order's actual total can't be automatically computed correctly."
            },
            {
                name: "reconciliation_notes",
                label: "Reconciliation notes",
                control: "textarea",
                    default: ""
            },
            {
                name: "invoice_date",
                label: "Invoice date",
                control: "datepicker",
                    options: {format: "yyyy-mm-dd"},
            },
            {
                name: "vendor",
                label: "Vendor",
                    control: ModelSelectControl,
                    room_model_module: SupplierChoices,
            },
            {
                name: "logistics_start",
                label: "Logistics start",
                control: "input",
                    type: "text"
            },
            {
                name: "logistics_end",
                label: "Logistics end",
                control: "input",
                    type: "text"
            },
            {
                name: "logistics_instructions",
                label: "Logistics instructions",
                control: "textarea"
            },
            {
                name: "notes",
                label: "Notes",
                control: "textarea"
            },
            {
                id: "submit",
                control: "button",
                label: "Save changes"
            }
        ];

        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'order',
		            template: template,
		            model: app.models.order,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
