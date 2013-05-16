
angular.module('programServices', ['ngResource']).
    factory('Program', function($resource){
            // 'rest/Program' uses appengine-rest-server's REST interface
  return $resource('/room/plain_models/Program', {}, {
          query: {method: 'GET', isArray: true}
  });
});

angular.module('userServices', ['ngResource']).
    factory('User', function($resource){
  return $resource('data/User', {}, {
    query: {method: 'GET'}
  });
});

angular.module('program_functions', ['programServices', 'userServices']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.
      when('/', 
           {controller:ProgramListCtrl, 
            templateUrl:'partials/program_list.html'}).
      when('/edit/:programId',
           {controller:ProgramEditCtrl, 
            templateUrl:'partials/program_detail.html'}).
      when('/new', 
           {controller:ProgramCreateCtrl, 
            templateUrl:'partials/program_detail.html'}).
      otherwise({redirectTo:'/'});
  }]);

function ProgramListCtrl($scope, $routeParams, Program, User) {
  // query() returns JSON like this 
  // [{"status": "Active", "site_number_prefix": "130"}, ... ]
  $scope.programs = Program.query();  
  $scope.user = User.query();

  $scope.IsSelectedProgram = function(program) {
      return program.key === $scope.user.program_selected;
  }; 
}

function ProgramEditCtrl($scope, $routeParams, Program, User) {
    $scope.whatsGoingOn = "Edit a Program";

}

function ProgramCreateCtrl($scope, $location, Program, User) {
    $scope.whatsGoingOn = "Create a new Program";
    $scope.save = function() {
        Program.save($scope.program, function(program) {
                $location.path('/');
            });
    }
}