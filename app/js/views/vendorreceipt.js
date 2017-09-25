define(
    [
	    'bootstrap-datepicker',
        'app/views/rooms_form',
	    'app/views/model_select_control',
        'app/models/captain_choices',
        'app/models/supplier_choices',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, RoomFormView, ModelSelectControl,
             CaptainChoice, SupplierChoice, template) {
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
                name: "state",
                label: "State",
                control: "select",
                options: [
                    {label: "new", value: "new"},
                    {label: "submitted", value: "submitted"},
                    {label: "payable", value: "payable"},
                    {label: "fulfilled", value: "fulfilled"},
                    {label: "deleted", value: "deleted"}
                ]
            },
            {
                name: "amount",
                label: "Purchase Amount ($)",
                control: "input"
            },
            {
                name: "purchase_date",
                label: "Purchase Date",
                control: "datepicker",
                    options: {format: "yyyy-mm-dd"},
                    required: true
            },
            {
                name: "captain",
                label: "Captain",
                    control: ModelSelectControl,
                    room_model_module: CaptainChoice
            },
            {
                name: "supplier",
                label: "Vendor",
                    control: ModelSelectControl,
                    room_model_module: SupplierChoice
            },
            {
                name: "description",
                label: "Description",
                control: "textarea"
            },
            {
                id: "submit",
                label: "Save changes",
                control: "button"
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
