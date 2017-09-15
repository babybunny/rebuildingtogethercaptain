define(
    ['backbone'],
    function(Backbone) {
        var Model = Backbone.Model.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.captain_',
            validate: function(attrs){
                if(!attrs.name){
                    this.errorModel.set({name: "Please enter captain name."})
                }
                if (!attrs.email){
                    this.errorModel.set({email: "Please enter captain email."})
                }
                if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                        return "Validation errors. Please fix.";
                }
            }
        });

        return Model;
    }
);
