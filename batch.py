from src.particletracker import track_gui, batchprocess
import os


if __name__ == '__main__':


    #path1 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\83g\\rock2000_2_anno\\down_2.MP4"
    ##path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\rock2000_2_anno\\down_3.MP4"
    #path3 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\rock2000_2_anno\\up_2.MP4"
    #path4 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\rock2000_2_anno\\up_3.MP4"

    path = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\575_TL.MP4"
    path1 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\rock2000Q\\up_1.MP4"
    

    #settings = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\10min_1in100_voroni.param"
    settings = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\parallel_nolink_10min.param"
    settingsanno = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\parallel_10min_1in5_anno.param"

    #batchprocess(path+"*.MP4", settings)
    #batchprocess(path1, settings)



    
    #batchprocess(path, settings)
    #print(f"processed {path}")
    
    #track_gui()
    track_gui(movie_filename=path)
    #track_gui(movie_filename="testdata/hydrogel.mp4",settings_filename = "testdata/temp.param")
