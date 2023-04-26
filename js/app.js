var app = angular.module('app', []);

app.controller('h5MacroController', function($scope) {
    var updateChoices = function() {
        $scope.callPythonDo({}).then(function(data) {
            $scope.model_path_choices = data.choices;
            if (!$scope.config.model_path) { // Set default value if none already set
                $scope.config.model_path = $scope.model_path_choices[0].value
            }
        }, function(data) {
            $scope.choices = [];
        });
    };
    
    var updateOutputModelPath = function (newValue, oldValue) {
        if (newValue !== oldValue) {
            $scope.config.output_model_path = $scope.config.model_path.replace(/\.[^/.]+$/, ".onnx")
        }
    }
    function fetchAccessibleFolders() {
        DataikuAPI.managedfolder.listWithAccessible($stateParams.projectKey).success(function (data) {
            data.forEach(folder => { folder.foreign = (folder.projectKey != $stateParams.projectKey); });
            data = data.filter(folder => !folder.foreign);
            $scope.accessibleFolders = data.map(ds => ({
                ref: ds.foreign ? (ds.projectKey + '.' + ds.id) : ds.id,
                displayName: ds.name + (ds.foreign ? ('(' + ds.projectKey + ')') : '')
            }));
            $scope.accessibleFoldersPlusEmpty = [{ref:'?', displayName:'Nothing selected'}].concat($scope.accessibleFolders);
        }).error(setErrorInScope.bind($scope.errorScope));
    }
    fetchAccessibleFolders();
    updateChoices();
    $scope.templatePath = $scope.templateUrl.substring(0, $scope.templateUrl.lastIndexOf("/")+1);
    
    $scope.$watch('config.input_folder_id', updateChoices, true);
    $scope.$watch('config.model_path', updateOutputModelPath, true);
});

app.controller('h5RecipeController', function($scope) {
    var updateChoices = function() {
        $scope.callPythonDo({}).then(function(data) {
            $scope.model_path_choices = data.choices;
            if (!$scope.config.model_path) { // Set default value if none already set
                $scope.config.model_path = $scope.model_path_choices[0].value
            }
        }, function(data) {
            $scope.choices = [];
        });
    };
    
    var updateOutputModelPath = function (newValue, oldValue) {
        if (newValue !== oldValue) {
            $scope.config.output_model_path = $scope.config.model_path.replace(/\.[^/.]+$/, ".onnx")
        }
    }

    updateChoices();
    
    $scope.templatePath = $scope.templateUrl.substring(0, $scope.templateUrl.lastIndexOf("/")+1);
    
    $scope.$watch('config.model_path', updateOutputModelPath, true);
    
});