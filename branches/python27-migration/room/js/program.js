
angular.module('programServices', ['ngResource']).
    factory('Program', function($resource){
            // 'rest/Program' uses appengine-rest-server's REST interface
  return $resource('plain_models/Program', {}, {});
});

angular.module('userServices', ['ngResource']).
    factory('User', function($resource){
  return $resource('data/User', {}, {});
});

angular.module('program_functions', ['programServices', 'userServices']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.
      when('/', 
           {controller:ProgramListCtrl, 
            templateUrl:'partials/program_list.html'}).
      when('/edit/:programKey',
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
  $scope.user = User.get();

  $scope.IsSelectedProgram = function(program) {
      return program.key === $scope.user.program_selected;
  }; 
  
  $scope.select = function(program, staff) {
      $scope.user.program_selected = program.key;
      $scope.user.$save();
  };
}

function ProgramCreateCtrl($scope, $location, Program, User) {
    $scope.whatsGoingOn = "Create a new Program";
    $scope.save = function() {
        Program.save($scope.program, function(program) {
                $location.path('/');
            });
    }
}

function ProgramEditCtrl($scope, $location, $routeParams, Program) {
    $scope.whatsGoingOn = "Edit a Program";
    var self = this;
 
    Program.get({key: $routeParams.programKey}, function(program) {
            self.original = program;
            $scope.program = new Program(self.original);
        });
    
    $scope.isClean = function() {
        return angular.equals(self.original, $scope.program);
    }
    
    $scope.destroy = function() {
        self.original.$destroy(function() {
                $location.path('/');
            });
    };
    
    $scope.save = function() {
        $scope.program.$save(function() {
                $location.path('/');
            });
    };
}