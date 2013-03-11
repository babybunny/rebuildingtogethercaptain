
angular.module('programServices', ['ngResource']).
    factory('Program', function($resource){
  return $resource('rest/Program', {}, {
    query: {method:'GET'}
  });
});

angular.module('userServices', ['ngResource']).
    factory('User', function($resource){
  return $resource('data/User', {}, {
    query: {method:'GET'}
  });
});

angular.module('program_functions', ['programServices', 'userServices']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.
      when('/', {templateUrl: 'partials/program_list.html',   controller: ProgramCtrl}).
        otherwise({redirectTo: '/phones'});  // huh?
  }]);

function ProgramCtrl($scope, $routeParams, Program, User) {
  // query() returns JSON like this 
  // {"list": {"Program": [{"status": "Active", "site_number_prefix": "130",
  $scope.program_query = Program.query();  
  $scope.user = User.query();

  $scope.IsSelectedProgram = function(program) {
     var yearname = program.year + ' ' + program.name;
     console.log('yn:"' + yearname + '" selected:"' + $scope.user.program_selected + '"');
     if (yearname === $scope.user.program_selected) {
       return true;
     }
     return false;
  }; 
}
