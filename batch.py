from src.particletracker import track_gui, batchprocess
import os


if __name__ == '__main__':


    path = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\live_tilt\\wobble2000\\11060001.MP4"
    #path1 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\live_tilt\\84g_y+4000\\11050002.MP4"
    #path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\live_tilt\\84g_y-4000\\11050001.MP4"

    path1 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\new_code_tests\\84g_550_static\\13930002.MP4"
    path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\new_code_tests\\84g_600_static\\13930001.MP4"

    settings = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\live_tilt\\test_med.param"


    #batchprocess(path1+"*.MP4", settings)

    #for path in [path1, path2]:
     # batchprocess(path, settings)
      #print(path + " done")

   
    #batchprocess(path+"*.MP4", settings)
    #track_gui()
    track_gui(movie_filename=path, settings_filename=settings)
    #track_gui(movie_filename="testdata/hydrogel.mp4",settings_filename = "testdata/temp.param")
