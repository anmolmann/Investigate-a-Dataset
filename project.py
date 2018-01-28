
# coding: utf-8

# ## Choosing Dataset:
# 
# **TMDb movie data**
# 
# *Questions*
# 
# 1. Which genres are most popular from year to year?
#     - (What changed between 2015 to 2016)
# 2. What kinds of properties are associated with movies that have high revenues?
#     - or what are the attributes of the movie with high revenues
#     - like What properties/attributes does the movies, which have done well at the box office, have?
#     - For Instance, Whether the popularity of the movie is dependent on the movie's budget?

# In[4]:


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('pylab', 'inline')


# In[5]:


# Load Data from a csv file
data = pd.read_csv("tmdb-movies.csv")


# In[6]:


data.head()


# In[7]:


data.info()


# In[8]:


# DATA WRANGLING

# cast, homepage, director, tagline, keywords, genres, production_companies columns have less than 10866 values
# so we will inspect these columns

data['homepage'] = data['homepage'].fillna('Homepage Unavailable')
data['cast'] = data['cast'].fillna('Information not available')
data['director'] = data['director'].fillna('Information not available')
data['tagline'] =data['tagline'].fillna('Will Update soon!')
data['keywords'] = data['keywords'].fillna('')
data['overview'] =data['overview'].fillna('Will Update soon!')
data['genres'] = data['genres'].fillna('NA')
data['production_companies'] = data['production_companies'].fillna('')
data['imdb_id'] = data['imdb_id'].fillna('NA')
# print(data['homepage'])
# data['imdb_id'].isnull().values.any()
# data['imdb_id'].isnull().sum()


# In[9]:


# data.info()
data.describe()

# so we can see that there is no revenue and budget for some of the movies

# count_budget = 0
# count_revenue = 0
# for i in range(len(data)):
#     count_budget = (count_budget + 1) if data.loc[i, 'budget'] == 0 else count_budget
#     count_revenue = (count_revenue + 1) if data.loc[i, 'revenue'] == 0 else count_revenue
# print(count_budget, count_revenue)


# ### Posing 1st Question
# 
# **Which genres are most popular from year to year?**

# In[10]:


# Range of release years
print("From: {} to {}.\n".format(data['release_year'].min(), data['release_year'].max()))
from_1960_to_2015 = range(data['release_year'].min(), data['release_year'].max() + 1)

genre_column = list(data["genres"])
genre_set = set()
for i in genre_column:
    row = i.split("|")
    for value in row:
        genre_set.add(value)
    
print(len(genre_set), genre_set)
# total -> 20 genres with one extra 'NA' genre which is substituted in place of the genres 
# with missing values in the original data


# In[11]:


# row by column dataframe of years by genres
years_by_genres = pd.DataFrame(index = from_1960_to_2015, columns = genre_set)
years_by_genres = years_by_genres.fillna(0)
years_by_genres.head()

for i in range(len(data)):
    genres_per_year = data.loc[i, 'genres'].split("|")
    year = data.loc[i, 'release_year']
    for val in genres_per_year:
        years_by_genres.loc[year, val] = years_by_genres.loc[year, val] + 1
        
years_by_genres.describe()


# #### These statistics clearly show that "Drama" genre is the most watched genre overall until now, followed by "Comedy" genre.
#     - So, the maximum number of movies fall in the category of Drama genre

# In[17]:


# Most popular genres from year to year
year_to_year = pd.Series(np.zeros(len(years_by_genres)), index=from_1960_to_2015)

# as i could see more than 1 genre having max values so i will individually loop through each row
for i in from_1960_to_2015:
    maximum = years_by_genres.max(axis=1).loc[i]
    genre_temp = "| "
    for j in genre_set:
        if maximum == years_by_genres.loc[i, j]:
            genre_temp = genre_temp + j + " | "
    year_to_year.loc[i] = genre_temp
    
print("Year\t\tPopular Genres\n\n{}".format(year_to_year))

# Pie chart for distribution of genres
genres_total = pd.Series(np.zeros(len(genre_set)), index = genre_set)
for j in genre_set:
    genres_total.loc[j] = years_by_genres[j].sum()
    
fig, axis = plt.subplots()
# top movies genre per year shown in pi chart
n = 10
distribution = genres_total.sort_values(ascending = False)[0:n]
genre_dist = list(distribution.keys())[0:n]
genre_dist.append("Others")
distribution.set_value("Others", (genres_total.sort_values(ascending=False).values)[n:].sum())
# print(distribution)
axis.pie(distribution, labels = genre_dist, autopct = '%1.1f%%', startangle = 90)
axis.axis('equal')
plt.title("Distribution of genres")
plt.show()


# In[20]:


genres_total.sort_values(ascending=False)[:5].plot(kind="pie",
                                                   autopct = '%1.1f%%',
                                                   title="Distribution of top 5 genres",
                                                   startangle = 0)


# In[21]:


# Distribution of Movies per year
for i in from_1960_to_2015:
    fig, axis = plt.subplots()
    # top 5 movies per year shown in pi chart
    n = 5
    distribution = years_by_genres.loc[i, :].sort_values(ascending = False)[0:n]
    genre_dist = list(distribution.keys())[0:n]
    axis.pie(distribution, labels = genre_dist, autopct = '%1.1f%%', startangle = 90)
    axis.axis('equal')
    plt.title("Percentage of movies in each genre in {}".format(i))
    plt.show()


# In[37]:


def standardize(x):
    x_standardized = (x - x.mean()) / x.std(ddof = 0)
    return x_standardized

# standardize popularity
std_pop =  standardize(data['popularity'])

# Exploring profit generated by the movies
profit = data['revenue'].sub(data['budget'], axis=0)

profit_temp = {'id': data['id'],
               'revenue': data['revenue'].values,
               'profits_per_movie': profit.values,
               'release_year': data['release_year'].values,
               'popularity': data['popularity'].values,
               'std_popularity': std_pop.values,
               'budget': data['budget'].values
                #'genres': data['genres'].values
              }

profitable_std_movies = pd.DataFrame(profit_temp)
profitable_std_movies.head()


# In[67]:


def grouping_data(x, column_name):
    return x.groupby(column_name)

# group data by release years
grouped_data_by_years = grouping_data(data, 'release_year')
grouped_profits_by_years = grouping_data(profitable_std_movies, 'release_year')

# standardize profits of movies per year
standardize(grouped_profits_by_years.sum()['profits_per_movie']).plot(title="Profits Distribution per year")
plt.ylabel("Standardized Profits")
plt.show()


# **We can visualize from the above plot that the profits made by the movie in the 2010-2015 years time period are lot more than the profits made by the movies earlier.**

# In[74]:


# checking whether the revenue collected for each movie is always higher than its budget or not
def mean_of_grouped_data(x, column_name):
    return x.mean()[column_name]

per_year_revenue = mean_of_grouped_data(grouped_data_by_years, 'revenue')
per_year_budget = mean_of_grouped_data(grouped_data_by_years, 'budget')

# finding correlation between revenue and budget per year
relation = (np.corrcoef(per_year_revenue, per_year_budget))[0, 1]
print("\nCorrelation between revenue and budget (of the movies per year): {}".format(relation))

# per_year_revenue.plot(label="Revenue")
# per_year_budget.plot(label="Budget")

plt.plot(from_1960_to_2015, per_year_revenue.values, label="Revenue")
plt.plot(from_1960_to_2015, per_year_budget.values, label="Budget")
plt.ylabel("Amount in $")
plt.xlabel("Release Years")
plt.title("Revenue & Budget Distribution")
plt.legend(loc='upper left')
plt.show()


# **As the coorelation between revenue and budget (per year) is approx. 0.9. It depicts that both the budget and revenue (variables) are strongly correlated. So, it might be possible that the movie with higher budget also has higher movie revenues. But as the data is not cleaned yet so we cannot assure anything.**
# 
# **We can also see from this plot that the revenue has been mostly higher than the budget of the movie but this does not suggest that the movies will almost always be profitable as in some cases, the revenue and the budget have also not been reported (as discussed earlier). So, it may be a possibility that some of theses movies could have faced losses.**

# In[48]:


# sort the table in descending order according to standardized popularity of the movies
profitable_std_movies = profitable_std_movies.sort_values(by='std_popularity', axis='index')
profitable_std_movies.head()


# In[63]:


def correlation(x, y):
    std_x = standardize(x)
    std_y = standardize(y)
    return (std_x * std_y).mean()

def bool_index(x, column_name):
    return x[column_name].values != 0

index = bool_index(data, 'budget')
popular_vs_budget = correlation(data['budget'].values[index],
                                data['popularity'].values[index])
print(popular_vs_budget)

temp = pd.Series(standardize(profitable_std_movies['popularity'].values[index]),
                 index=[standardize(profitable_std_movies['budget'].values[index])])
temp.plot(title="Popularity vs Budget Distribution")
plt.ylabel("Popularity")
plt.xlabel("Movie Budget in $")
plt.show()


# **From the above correlation, we can observe that the value 0.48 approx. is positive which depicts a strong relaitonship between budget and popularity of the movie.**
# 
# **Also, the graph shows us the same thing that when the budget (along the x-axis) of the movies increases, the popularity of the also increases. But this graph can be also misleading as the testing values are reduced to half in this case.**

# In[64]:


index = bool_index(profitable_std_movies, 'revenue')

popular_vs_rev = (np.corrcoef((profitable_std_movies['revenue'].values)[index],
                              (profitable_std_movies['popularity'].values)[index]))[0, 1]
print(popular_vs_rev)
temp = pd.Series(standardize(profitable_std_movies['popularity'].values[index]),
                 index=[standardize(profitable_std_movies['revenue'].values[index])])
temp.plot(title="Popularity vs Revenue Distribution")
plt.ylabel("Popularity")
plt.xlabel("Movie Revenue in $")
plt.show()


# #### So, from the above correlation values 0.63 approx., between variables revenue and std_popularity, we can see that it is close to +1. Hence, we can see that there is a some STRONG relation between revenue and popularity. Because the Correlation value is > 0, which suggests that if one variable increases with certain margin the other will also increase with approx. similar margin as well. 
# *We can say that revenue and popularity are closely and positively correlated.*

# In[371]:


index = bool_index(profitable_std_movies, 'profits_per_movie')

popular_vs_profit = (np.corrcoef((profitable_std_movies['profits_per_movie'].values)[index],
                                 (profitable_std_movies['popularity'].values)[index])
                    )[0, 1]
print(popular_vs_profit)


# **Here, we can see that the variables profits_per_movie and std_popularity are also positively correlated (close to +1) which implies a STRONG relationship between both the variables. So, it may be a possibility that if a movie is more popular it may be more profitable also or vice versa. But not in all cases.**

# # SUMMARY
# 
# 1. The most popular genre from year to year is DRAMA (with a total of 17.6% drama movies) followed by Comedy (14.1%) as depicted by the plots above.
# 2. properties/attributes of the movies which are more popular:
#     - We could see that some of the values in the budget (column) were 0. So, we did not include those 0 values for finding a similarity in our data. (Data Cleaning)
#     - We found the similarity in our data by using Pearson's coefficient.
#     - by the correlation value ablove, we can say that the budget of the movies contributes to the popularity of the movie at the box office, but 0.48 value is not a strong evidence to say so. So, it may or may not be the factor in some cases.
#     - Similarly, we can also say that the revenue collected and the profit per movie can also be the factors or reasons towards the popularity of the movie as the correlation values for these variables with popularity variable are also positive and above 0.60. 
#     - We are **tentatively** concluding above points but we don't have any concrete results as the correlation values are positive but not so close to +1.
#     
# **LIMITATIONS**
#     - Incomplete Data: - Missing values, even the lack of a section like budget in this case (or a substantial part of the data), could limit its usability.
#     - Due to lack of data regarding budget (as some fields were 0, thus, having no budget at all to analyse) we cannot entirely depend up on the data remaining after data cleaning to determine whether the above stated relationship is correct or not.
#     - Because from the cleaned dataset we arrived at the (budget-popularity, revenue-popularity) relationship and since, almost half the dataset was removed dut to the unavailability of budget details, the above stated relationship is partially true.
#     - So, the lack of budget data also makes our data analysis less reliable.
# 
# **FUTURE PLANS**
# 
# The report covers only some of the parameters like genres and release_years; revenue & popularity; budget & popularity, etc. There are many more parameters available in the data which can be analysed and expored further.
#     - We can expore the vote count parametre a liitle more and check its relationship with the popularity parameter.
#     - We can also see whether the cast plays any role in the revenue collection of a movie and the popularity of the movie or even in the vote count.
#     
