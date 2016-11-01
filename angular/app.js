(function() {
    var app = angular.module('movies', []);

    app.controller('MovieController', ['$http', function($http){
        var that = this;
        this.search = '';
        this.results = [];
        this.recommendations = [];
        this.lookup = function(){
            if (this.search === '')
                return;
            var data = $.param({
                query: that.search
            });
            $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
            $http.post('http://localhost:8000/ml/search_movies/', data)
            .success(function(data) {
                that.results = data;
            });
        };

        this.recommend = function(){
            $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
            $http.post('http://localhost:8000/ml/get_recommendations/')
            .success(function(data) {
                that.recommendations = data;
            });
        };

        this.tab = 1;
        this.setTab = function(tab){
            this.tab = tab;
        };
        this.isSet = function(tab){
            return this.tab === tab;
        };
    }]);

    app.controller('RateController', ['$http', function($http){
        this.rating = 5;
        this.rate = function(movie_id, searchCtrl){
            var data = $.param({
                movie_id: movie_id,
                rating: this.rating
            });
            $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
            $http.post('http://localhost:8000/ml/rate_movie/', data)
            .success(function(data) {
                searchCtrl.lookup();
                return data['success'];
            });
        };
    }]);

    app.controller('SettingsController', ['$http', function($http){
        this.resetRatings = function(){
            $http.post('http://localhost:8000/ml/clear_ratings/')
            .success(function(data) {
                return data;
            });
        };
    }]);
})();
