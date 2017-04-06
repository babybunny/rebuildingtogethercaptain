define(function() {
  var User = Backbone.Model.extend({
    // matches first part of 'name' in @endpoints.method
    url: 'current_user'
  });

  return User;
});
