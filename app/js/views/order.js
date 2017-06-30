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
            // boilerplate
            {
                name: "site",
                label: "Site",
                control: "input",
                disabled: true
            },
            {
                name: "order_sheet",
                label: "Order sheet",
                control: "input",
                disabled: true
            },
            {
                name: "state",
                label: "State",
                control: "input",
            },
            {
                name: "logistics_instructions",
                label: "Logistics instructions",
                control: "textarea",
            },
            {
                name: "logistics_start",
                label: "Logistics start",
                control: "input",
            },
            {
                name: "logistics_end",
                label: "Logistics end",
                control: "input",
            },
            {
                name: "vendor",
                label: "Vendor",
		            control: ModelSelectControl,
		            room_model_module: SupplierChoices,
            },
            {
                name: "invoice_date",
                label: "Invoice date",
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
            },
            {
                name: "notes",
                label: "Notes",
                control: "textarea",
            },
            {
                name: "reconciliation_notes",
                label: "Reconciliation notes",
                control: "textarea",
            },
            {
                name: "actual_total",
                label: "Actual total",
                control: "input",
                helpMessage: "Use this is in the rare case when the order's actual total can't be automatically computed correctly."
            },
            {
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