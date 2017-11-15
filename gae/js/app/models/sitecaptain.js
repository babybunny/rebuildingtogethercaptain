define(
    ['backbone'],
    function(Backbone) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/cru_api.sitecaptain_',
            validate: function(attrs, options){
                this.errorModel.clear();

                if (!attrs.captain){
                    this.errorModel.set({captain: 'Please select a captain.'})
                }
                if (!attrs.type){
                    this.errorModel.set({type: 'Please select captain type.'})
                }
                if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                    return "Validation errors. Please fix.";
                }

            }
        });

        return Model;
    }
);
