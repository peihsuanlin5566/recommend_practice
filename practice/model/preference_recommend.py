from statistics import variance
from practice.data.ratings import Ratings
from practice.data.genome_scores import GenomeScores 
from practice.data.genome_tags import GenomeTags 
from practice.data.movies import Movies 
from practice.model.recommend import Recommend
import numpy as np 
from numpy.linalg import norm
import time 


class PreferenceRecommend( Recommend ): 
    
    def __init__(self):
        super().__init__()
    
        self.genome_scores = GenomeScores.from_csv() 
        self.genome_tags =  GenomeTags.from_csv()
        

    def i_rated(self, user_id) -> int:
        user_ratings = self.ratings.get_ratings(user_id)
        return len(user_ratings)
        
    def it_rated(self, user_id, tag_id) -> int: 
        user_ratings = self.ratings.get_ratings(user_id)
        movie_id_list = [ x.movieId for x in user_ratings if tag_id in self.genome_scores.get_tags_by_movieid(x.movieId) ]

        return len(movie_id_list)

    def i(self, ) -> int:  
        return len(Movies.from_csv(csv_file_name='csv/movies.csv').movie_list)

    def it(self,tag_id ) -> int: 
        self.genome_scores.set_movieid_by_tags()
        movieid_by_tags_list = self.genome_scores.get_movieid_by_tagid(tag_id)
        return len(movieid_by_tags_list)

    def wit(self, movie_id, tag_id) -> int: 
        self.genome_scores.set_movieid_by_tags()
        movieid_by_tags_list = self.genome_scores.get_movieid_by_tagid(tag_id)
        if movie_id in movieid_by_tags_list: 
            return 1
        return 0


    def rt_vec(self, user_id) -> dict: 
        user_ratings = self.ratings.get_ratings(user_id)
        movie_ids = [ user_rating.movieId for user_rating in user_ratings ]
        rt = { }
        for movie_id in movie_ids: 
            tags = self.genome_scores.get_tags_by_movieid(movie_id)
            for tag_id in tags:
                if tag_id not in rt:
                    rt[tag_id] = []
                rt[tag_id].append(self.ratings.get_ratings_by_movies(movie_id, user_id))
        return rt


    def ni_plus(self, movie_id) -> float: 
        rating_by_movieid = self.ratings.get_ratings_by_movieid(movie_id)
    
        return len([ 1  for rating_item in  rating_by_movieid if rating_item.rating > 3  ]) 


    def ni_minus(self, movie_id) -> float: 
        rating_by_movieid = self.ratings.get_ratings_by_movieid(movie_id)
    
        return len([ 1  for rating_item in  rating_by_movieid if rating_item.rating <= 3  ]) 

    def equation1(self, user_id ) -> dict:
        rt_vec = self.rt_vec(user_id)
        rt = {}
        for tag_id in rt_vec.keys(): 
            it = self.it_rated(user_id, tag_id)
            rt[tag_id] = sum(rt_vec[tag_id])/it

        return rt
    
    def equation2(self, user_id) -> dict: 

        rt = self.equation1(user_id)
        user_ratings = self.ratings.get_ratings(user_id)
        user_ratings_ratings = [rating.rating for rating in user_ratings]
        r_mu = sum(user_ratings_ratings)/len(user_ratings_ratings)
        
        wt = {}
        for tag_id in rt.keys(): 
            wt[tag_id] = rt[tag_id] -  r_mu

        return wt 
    
    def equation4(self, user_id, tag_id) -> float: 

        #  U = cov * sig * |wt|
        
        cov = self.equation5(user_id, tag_id)
        sig = self.equation6(user_id, tag_id)
        wt_abs = abs(self.equation2(user_id)[tag_id]) 
        
        return cov*sig*wt_abs

    
    def equation5(self, user_id, tag_id) -> float: 

        i   = self.i_rated(user_id)
        it  = self.it_rated( user_id, tag_id)
        
        return min([  it/i , (i-it)/ i  ])
        
    
    def equation6(self, user_id, tag_id) -> float:
        
        wt_abs = abs(self.equation2(user_id)[tag_id]) 
        
        Rt = self.rt_vec(user_id)[tag_id]
        sigma_t = self.variance(Rt)
        it = self.it_rated( user_id, tag_id)
        
        return min(  [2, wt_abs/(sigma_t/np.sqrt(it))] )


    def variance(self, data, ddof=0) -> float:
        n = len(data)
        mean = sum(data) / n
        return sum((x - mean) ** 2 for x in data) / (n - ddof)


    def equation9(self, user_id ) -> int:
        self.genome_tags.set_tagId_list()
        tagId_list = self.genome_tags.tagId_list
        s_list = [ self.equation4(user_id, tagId) for tagId in tagId_list ]

        return np.argmax(s_list)

    def equation17(self, movie_id, tag_id, mu=1): 
        wit = self.wit(movie_id, tag_id, )
        it = self.it(tag_id)
        i = self.i()

        return ( wit + mu*it/ i ) / ( mu + i/it)


    def equation22(self, user_id, movie_id ): 
        ni_plus = self.ni_plus(movie_id)
        ni_minus = self.ni_minus(movie_id)

        ...
        
    