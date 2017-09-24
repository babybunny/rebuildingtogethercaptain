define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.vendorreceipt_',
	          must_be_floats: ['amount'],

              defaults: {
                  state: "new"
              },
              validate: function(attrs){
                //   In 'old forms.py' (ln. 234) purchase_date is required.
                //   Is it ok to keep this here even though purchase_date is not a required prop in ndb_models?
                  if(!attrs.purchase_date){
                      this.errorModel.set({purchase_date: " Please enter purchase date."})
                  }
                  if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                      return "Validation errors. Please fix.";
                  }
              }
        });

        return Model;
    }
);
