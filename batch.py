from src.particletracker import track_gui, batchprocess
import os


if __name__ == '__main__':

  


    path = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\new_code_tests\\84g_600_static\\13930001.MP4"
    #path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\4K_50p\\625\\"
    path3 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\4K_50p\\700-650Q\\"
    settings = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\new_code_tests\\testfull_nolink_noanno_6tj.param"

    #batchprocess(path1+"*.MP4", settings)

    #for path in [path1, path3]:
      #batchprocess(path+"*.MP4", settings)
      #print(path + " done")

   
    #batchprocess(path+"*.MP4", settings)
    #track_gui(movie_filename=path, settings_filename=settings)
    track_gui(movie_filename="testdata/hydrogel.mp4",settings_filename = "testdata/test_hydrogel.param")
