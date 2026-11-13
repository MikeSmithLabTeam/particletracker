from src.particletracker import track_gui, batchprocess
import os


if __name__ == '__main__':


    #path1 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\83g\\rock2000_2_anno\\down_2.MP4"
    ##path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\rock2000_2_anno\\down_3.MP4"
    #path3 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\rock2000_2_anno\\up_2.MP4"
    #path4 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\rock2000_2_anno\\up_3.MP4"

    #path = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\84g\\T_Y_TL\\sliced\\"
 
    #path1 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\84g\\12h_static\\4400_-2000_r\\part_1.MP4"
    #path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\84g\\12h_static\\4400_-2000_r\\part_2.MP4"   
  
    path = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\85g\\12h_static\\4400_-2000\\"
    path1 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\85g\\12h_static\\4400_-2000\\4400_-2000.MP4"    
    #path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\86g\\12h_static\\4400_-5000\\part_2.MP4"
    
    

    #settings = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\10min_1in100_voroni.param"
    #settings = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\84g\\weekend_leveling\\old_tj_median.param"
    settings = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\84g\\12h_static\\12h_tl.param"
    #settingsanno = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\parallel_10min_1in5_anno.param"

    
    
    # print("\n ======================================\n "+ path1 + '  start \n ====================================== \n')  
    #batchprocess(path1, settings)

    # print("\n ======================================\n "+ path2 + '  start \n ====================================== \n')    
    # batchprocess(path2, settings)

    #print("\n ======================================\n "+ path + '  start \n ====================================== \n') 
    
    #batchprocess(path+"*.MP4", settings)



    
    #batchprocess(path, settings)
    #print(f"processed {path}")
    # batchprocess(path1, settings2)
    # print(f"processed {path}")
    
    #track_gui()
    track_gui(movie_filename=path1, settings_filename=settings)
    #track_gui(movie_filename="testdata/hydrogel.mp4",settings_filename = "testdata/temp.param")
