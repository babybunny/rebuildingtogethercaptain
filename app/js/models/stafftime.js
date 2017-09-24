define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.stafftime_',
	          must_be_floats: ['hours', 'miles'],
              defaults: {
                  state: "new"
              },
              validate: function(attrs){
                //   Luke, Since site is explicitly required I put the validation here,  but is it really necessary?
                //   (site is disabled & autopopulates)
                  if (!attrs.site) {
                      this.errorModel.set({site: "Please associate a site with this stafftime submission."})
                  }
                  // Required to calculate HoursTotal/ MileageTotal
                  if(!attrs.activity_date){
                      this.errorModel.set({activity_date: " Please enter activity date."})
                  }
                  // Required to calculate HoursTotal/ MileageTotal
                  if(!attrs.position){
                      this.errorModel.set({position: " Please enter staff position."})
                  }
                  if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                      return "Validation errors. Please fix.";
                  }
              }
          });
          return Model;
      }
  );
