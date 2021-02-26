from particletracker.general.dataframes import DataStore
import numpy as np

if __name__ == '__main__':
    ds = DataStore('/home/ppzmis/Documents/PythonScripts/particletracker/particletracker/testdata/hough.hdf5',load=True)
    df = ds.df
    ds2 = DataStore(
        '/home/ppzmis/Documents/PythonScripts/particletracker/particletracker/testdata/hough_temp.hdf5',
        load=True)
    df2 = ds2.df

    #Annoyingly the linking code creates an index and a column called frame.
    df.index.name = 'frame_index'
    #print(np.size(df2['particle']))

    for i in range(df.index.max()):
        print(np.size(df[df.index == i]['particle']))

    #View the data
    print(df) # Print data
    print(df.head(n=20)) #Print first 20 rows
    print(df.tail()) #Print last 5

    #View a column
    print(df['intensities'])

    #View 2 columns
    print(df[['x','y']])


    #Everything below here requires you to have processed multiple frames into a dataframe

    #Get intensities of all particles in 1 frame
    print(df[df.index == 1].intensities)

    #Get mean intensity of all particles in particular frame
    print(df[df.index == 1].intensities.mean())

    #Get intensities of 1 particle in all frames
    df.set_index('particle', inplace=True)
    df.sort_index(inplace=True)
    print(df[df.index == 3].intensities)

    #At this point if you wanted the intensities of all particles in 1 frame
    #you need to switch the index back
    df.set_index('frame', inplace=True)
    df.sort_index(inplace=True)
    print(df[df.index == 1].intensities)






