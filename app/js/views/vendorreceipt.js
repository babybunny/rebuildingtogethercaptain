define(
    [
	'bootstrap-datepicker',
        'app/views/rooms_form',
	'app/views/model_select_control',
        'app/models/captain_choices',
        'app/models/supplier_choices',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, RoomFormView, ModelSelectControl, CaptainChoices, SupplierChoices, template) {
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
                name: "purchase_date",
                label: "Purchase date",
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
            },
            {
                name: "amount",
                label: "Amount",
                control: "input",
            },
            {
                name: "vendor",
                label: "Vendor",
                control: "input",
            },
            {
                name: "supplier",
                label: "Supplier",
		control: ModelSelectControl,
		room_model_module: SupplierChoices,
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
		name: 'vendorreceipt',
		template: template,
		model: app.models.vendorreceipt,
		loading: loading,
		fields: fields,
	    });
        }
        return ViewFactory;
    }
)
