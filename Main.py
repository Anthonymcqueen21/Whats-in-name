column names: year, age, qx, lx, dx, Lx, Tx, ex, sex"""\n    assert all(name in lifetables_2016 for name in [\'year\', \'age\', \'qx\', \'lx\', \'dx\', \'Lx\', \'Tx\', \'ex\', \'sex\']), \\\n      "Your DataFrame, lifetables_2016, should have columns named: year, age, qx, lx, dx, Lx, Tx, ex, sex."\n\ndef test_lifetables_2016_df_year_plus_age():\n    """Output has the year + age = 2016"""\n    assert all(lifetables_2016.year + lifetables_2016.age - 2016 == 0), \\\n      "The `year` column and `age` column in `lifetables_2016` should sum up to 2016."')


# ## 7. Smoothen the Curve!
# <p>We are almost there. There is just one small glitch. The cohort life tables are provided only for every decade. In order to figure out the distribution of people alive, we need the probabilities for every year. One way to fill up the gaps in the data is to use some kind of interpolation. Let us keep things simple and use linear interpolation to fill out the gaps in values of <code>lx</code>, between the years <code>1900</code> and <code>2016</code>.</p>

# In[35]:


# Create smoothened lifetable_2016_s by interpolating values of lx
import numpy as np

# create numpy array for new year index
year = np.arange(1900, 2016)
#create dfs for sex in dict
mf = {"M": pd.DataFrame(), 'F': pd.DataFrame()}

# iterate over sexs
for sex in ['M', 'F']:
    # filter table to only relevent sex and columns
    df = lifetables_2016[lifetables_2016.sex == sex][['year', 'lx']]
    # chain methods to set year as index, reindex using numpy array, interpolate
    mf[sex] = df.set_index('year').reindex(year).interpolate().reset_index()
    # set sex column to current iteration
    mf[sex]['sex'] = sex
    
# concat dfs
lifetable_2016_s = pd.concat(mf, ignore_index = True)

print(lifetable_2016_s.head())

# Plot the morality by sex with smoothing
# initialize subplouts
fig, ax = plt.subplots(figsize=(8,6))

# iterator over id and group objects
for id, group in lifetable_2016_s.groupby('sex'):
    #plot each with the label matching id
    group.plot(x = 'year', y = 'lx', kind = 'line', ax = ax, label = id)
plt.show()


# In[36]:


get_ipython().run_cell_magic('nose', '', 'def test_lifetable_2016_s_exists():\n    """lifetable_2016_s is defined"""\n    assert \'lifetable_2016_s\' in globals(), \\\n      "You should have defined a variable named lifetable_2016_s."\ndef test_lifetables_2016_s_df():\n    """lifetable_2016_s is a dataframe with 232 rows and 3 columns."""\n    assert lifetable_2016_s.shape == (232, 3), \\\n      "Your DataFrame, lifetable_2016_s, should have 232 rows and 3 columns."\n\ndef test_lifetable_2016_s_df_colnames():\n    """lifetable_2016_s has column names: year, lx, sex"""\n    assert all(name in lifetable_2016_s for name in [\'year\', \'lx\', \'sex\']), \\\n      "Your DataFrame, lifetable_2016_s, should have columns named: year, lx, sex."')


# ## 8. Distribution of People Alive by Name
# <p>Now that we have all the required data, we need a few helper functions to help us with our analysis. </p>
# <p>The first function we will write is <code>get_data</code>,which takes <code>name</code> and <code>sex</code> as inputs and returns a data frame with the distribution of number of births and number of people alive by year.</p>
# <p>The second function is <code>plot_name</code> which accepts the same arguments as <code>get_data</code>, but returns a line plot of the distribution of number of births, overlaid by an area plot of the number alive by year.</p>
# <p>Using these functions, we will plot the distribution of births for boys named <strong>Joseph</strong> and girls named <strong>Brittany</strong>.</p>

# In[37]:


df = bnames.merge(lifetable_2016_s)
df['n_alive']=df['lx']/100000*df['births']

def get_data(name, sex):
    '''retrives data from merged lifetable and bnames for particular name and sex'''
    df1 = df[df.name==name]
    df2 = df1[df1.sex == sex]
    return df2

def plot_data(name, sex):
    fig, ax = plt.subplots()
    dat = get_data(name, sex)
    dat.plot(x = 'year', y='births', ax = ax, color = 'black')
    dat.plot(x = 'year', y ='n_alive', kind = 'area', ax = ax, color = 'steelblue',alpha = 0.8)
    ax.set_xlim(1900, 2016)
    plt.title('Distribution of births for the name: ' + name + '('+sex+')')
    plt.show()
    #return 


# Plot the distribution of births and number alive for Joseph and Brittany
plot_data('Brittany','F')
plot_data('Joseph', 'M')


# In[38]:


get_ipython().run_cell_magic('nose', '', 'joseph = get_data(\'Joseph\', \'M\')\ndef test_joseph_df():\n    """get_data(\'Joseph\', \'M\') is a dataframe with 116 rows and 6 columns."""\n    assert joseph.shape == (116, 6), \\\n      "Running  get_data(\'Joseph\', \'M\') should return a data frame with 116 rows and 6 columns."\n\ndef test_joseph_df_colnames():\n    """get_data(\'Joseph\', \'M\') has column names: name, sex, births, year, lx, n_alive"""\n    assert all(name in lifetable_2016_s for name in [\'year\', \'lx\', \'sex\']), \\\n      "Running  get_data(\'Joseph\', \'M\') should return a data frame with column names: name, sex, births, year, lx, n_alive"')


# ## 9. Estimate Age
# <p>In this section, we want to figure out the probability that a person with a certain name is alive, as well as the quantiles of their age distribution. In particular, we will estimate the age of a female named <strong>Gertrude</strong>. Any guesses on how old a person with this name is? How about a male named <strong>William</strong>?</p>

# In[39]:


# Import modules
from wquantiles import quantile

# Function to estimate age quantiles
def estimate_age(name, sex):
    data = get_data(name,sex)
    qs = [0.75, 0.5, 0.25]
    quantiles = [2016-int(quantile(data.year,data.n_alive, q)) for q in qs]
    result = dict(zip(['q25', 'q50', 'q75'],quantiles))
    result['p_alive']=round(data.n_alive.sum()/data.births.sum()*100,2)
    result['sex']=sex
    result['name']=name
    return pd.Series(result)

# Estimate the age of Gertrude
estimate_age('Gertrude','F')


# In[40]:


get_ipython().run_cell_magic('nose', '', 'gertrude = estimate_age(\'Gertrude\', \'F\')\ndef test_gertrude_names():\n    """Series has indices name, p_alive, q25, q50 and q75"""\n    expected_names = [\'name\', \'p_alive\', \'q25\', \'q50\', \'q75\']\n    assert all(name in gertrude.index.values for name in expected_names), \\\n      "Your function `estimate_age` should return a series with names: name, p_alive, q25, q50 and q75"\n\ndef test_gertrude_q50():\n    """50th Percentile of age for Gertrude is between 75 and 85"""\n    assert ((75 < gertrude[\'q50\']) and (gertrude[\'q50\'] < 85)), \\\n      "The estimated median age for the name Gertrude should be between 75 and 85."')


# ## 10. Median Age of Top 10 Female Names
# <p>In the previous section, we estimated the age of a female named Gertrude. Let's go one step further this time, and compute the 25th, 50th and 75th percentiles of age, and the probability of being alive for the top 10 most common female names of all time. This should give us some interesting insights on how these names stack up in terms of median ages!</p>

# In[41]:


# Create median_ages: DataFrame with Top 10 Female names,
names_F = bnames[bnames.sex == "F"]
del names_F['year']
names_F_grouped = names_F.groupby('name').sum()
names_F_sorted = names_F_grouped.sort('births', ascending = False)
top_10_names_F= names_F_sorted.head(10)
top_10_names_F = top_10_names_F.reset_index()
top_10_names_F

#    age percentiles and probability of being alive
estimates = pd.concat([estimate_age(name, 'F') for name in top_10_names_F.name], axis = 1)
median_ages = estimates.T.sort_values('q50').reset_index(drop=True)


# In[42]:


get_ipython().run_cell_magic('nose', '', 'def test_median_ages_exists():\n    """median_ages is defined"""\n    assert \'median_ages\' in globals(), \\\n      "You should have a variable named median_ages defined."\ndef test_median_ages_df():\n    """median_ages is a dataframe with 10 rows and 6 columns."""\n    assert median_ages.shape == (10, 6), \\\n      "Your DataFrame, median_ages, should have 10 rows and 6 columns"\n\ndef test_median_ages_df_colnames():\n    """median_ages has column names: name, p_alive, q25, q50, q75 and sex"""\n    assert all(name in median_ages for name in [\'name\', \'p_alive\', \'q25\', \'q50\', \'q75\', \'sex\']), \\\n      "Your DataFrame, median_ages, should have columns named: name, p_alive, q25, q50, q75 and sex"')

