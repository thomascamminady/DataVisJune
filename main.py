import os
import geopandas #to install: pip install git+git://github.com/geopandas/geopandas.git
import matplotlib
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Read data
df2015 = pd.read_csv("2015.csv")
df2016 = pd.read_csv("2016.csv")
df2017 = pd.read_csv("2017.csv")

# Add year
df2015['Year'] = 2015
df2016['Year'] = 2016
df2017['Year'] = 2017

# Naming convention for the df2017 is slightly off, we fix this.
df2017.rename(columns={
    'Happiness.Rank': 'Happiness Rank',
    'Happiness.Score': 'Happiness Score',
    'Whisker.low': 'Whisker low',
    'Whisker.high': 'Whisker high',
    'Economy..GDP.per.Capita.': 'Economy (GDP per Capita)',
    'Health..Life.Expectancy.': 'Health (Life Expectancy)',
    'Trust..Government.Corruption.': 'Trust (Government Corruption)',
    'Dystopia.Residual':'Dystopia Residual'
    },inplace=True)

# Merge together
df = df2015.merge(df2016,how='outer').merge(df2017,how='outer')

# We rename some countries so they correspond to the naming in geopandas alter on
df.rename(columns={"Country":"name"},inplace=True)

old = ['Ivory Coast','Palestinian Territories','Bosnia and Herzegovina','Congo (Kinshasa)','Czech Republic','Central African Republic',
      'United States','Dominican Republic','Somaliland region']
new = ["Côte d'Ivoire",'Palestine','Bosnia and Herz.','Dem. Rep. Congo','Czechia','Central African Rep.',
      'United States of America','Dominican Rep.','Somalia']

for pos,o in enumerate(old):
    df.loc[df.name == o, "name" ] = new[pos]


# This may take some seconds..


# Create directory for figure output
os.system("mkdir -p figs")

for year in [2015,2016,2017]:
    for item in ['Happiness Rank','Happiness Score','Economy (GDP per Capita)','Health (Life Expectancy)','Trust (Government Corruption)','Freedom',
            "Generosity",'Family','Dystopia Residual']:
    
        # Take world data from geopandas and merge with our data
        world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
        world = world[(world.name != "Antarctica") & (world.name != "Fr. S. Antarctic Lands")]
        #world = world.to_crs({'init': 'epsg:3395'}) # world.to_crs(epsg=3395) would also work

        # Filter by year
        dff = df.loc[df.Year == year].copy()
        # Merge
        world = world.merge(dff.filter(items=['name',item]),how='left',on='name')
        world.dropna(inplace=True)
        
        # Create figure and plot
        fig, ax = plt.subplots(1,1,figsize=(1920/50,1080/50))
        ax.axis('off')
        cmap = "RdYlGn_r" if item=="Happiness Rank" else "RdYlGn"
        world.plot(column=item,cmap=cmap,ax=ax, legend=False)
        ax.set_title("{}".format(item),fontsize=100)
        
        # Deal with colorbar    
        sm = plt.cm.ScalarMappable(cmap=cmap,norm=plt.Normalize(vmin=min(world[item]), vmax=max(world[item])))
        sm._A = []
        cbar = fig.colorbar(sm,orientation="horizontal", pad=0,shrink=0.5)
        cbar.ax.tick_params(labelsize=70)
        
        # Save figure
        plt.savefig("figs/{}_{}.png".format(item.replace(" ","_"),year),bbox_inches='tight',dpi=100)
        plt.close()
        
    # Combine the plots via montage. This could also be done with subplots I guess...
    comm = "montage -density 100 -tile 3x4 -geometry +40+200 figs/*{}.png {}_overview.png".format(year,year)
    os.system(comm)
    
    
for year in [2015,2016,2017]:
    comm = """convert -font helvetica -fill black -pointsize 100 -draw "text 15,5900 'Happiness Report {}, Author: Thomas Camminady, Data Source: https://www.kaggle.com/henosergoyan/happiness/data'" {}_overview.png {}_overview.png""".format(year,year,year)    
    print(comm)
    os.system(comm)
