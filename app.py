import flask
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from omdbapi.movie_search import GetMovie

app = flask.Flask(__name__, template_folder='templates')

df2 = pd.read_csv('./model/tmdb.csv')

count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df2['soup'])

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

df2 = df2.reset_index()
indices = pd.Series(df2.index, index=df2['title'])
all_titles = [df2['title'][i] for i in range(len(df2['title']))]

def get_recommendations(title):
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    tit = df2['title'].iloc[movie_indices]
    dat = df2['release_date'].iloc[movie_indices]
    return_df = pd.DataFrame(columns=['Title','Year','Plot','Ratings','Genre'])
    return_df['Title']=tit
    return_df['Year']=dat
    plo = []
    gen = []
    rat = []
    for i in tit:
        movie = GetMovie(title=i, api_key='c938d4f0')
        mov = movie.get_data('Genre','Ratings','Plot')
        plo.append(mov['Plot'])
        rat.append(mov['Ratings'][0]['Value'])
        gen.append(mov['Genre'])
    return_df['Plot']=plo
    return_df['Ratings']=rat
    return_df['Genre']=gen
    return return_df

# Set up the main route
@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
         
    if flask.request.method == 'POST':
        m_name = flask.request.form['movie_name']
        m_name = m_name.title()
        if m_name not in all_titles:
            return(flask.render_template('not_found.html',name=m_name))
        else:
            result_final = get_recommendations(m_name)
            names = []
            dates = []
            plots = []
            ratings = []
            genre = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                dates.append(result_final.iloc[i][1])
                plots.append(result_final.iloc[i][2])
                ratings.append(result_final.iloc[i][3])
                genre.append(result_final.iloc[i][4])

            return flask.render_template('recommend.html',movie_names=names,movie_date=dates,movie_plot=plots,movie_rating=ratings,movie_genre=genre,search_name=m_name)

if __name__ == '__main__':
    app.run(debug=True)
