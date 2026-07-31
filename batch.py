from src.particletracker import track_gui, batchprocess
import os


if __name__ == '__main__':

    #path = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\new_code_tests\\84g_600_static\\13930001.MP4"
    #path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\4K_50p\\625\\"
    #path3 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\4K_50p\\700-650Q\\"
    #settings = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\new_code_tests\\84g_600_static\\test_new_hexatic.param"

    path1 = "Y:\\Joe_shaker1\\grain_boundarys\\Triple_H\\new_code_tests\\84g_550_static\\13930002.MP4"
    path2 = "Y:\\Joe_shaker1\\grain_boundarys\\Triple_H\\new_code_tests\\84g_600_static\\13930001.MP4"
    path3 = "Y:\\Joe_shaker1\\grain_boundarys\\Triple_H\\new_code_tests\\84g_600_static+2000\\13930004.MP4"
    path4 = "Y:\\Joe_shaker1\\grain_boundarys\\Triple_H\\new_code_tests\\84g_600_static-2000\\13930005.MP4"

    settings = "Y:\\Joe_shaker1\\grain_boundarys\\Triple_H\\new_code_tests\\testfull_link_noanno_5tj.param"


    #batchprocess(path1+"*.MP4", settings)

    #for path in [path1, path2, path3, path4]:
    #  batchprocess(path, settings)
    #  print(path + " done")

   
    #batchprocess(path+"*.MP4", settings)
    #track_gui()
    track_gui(movie_filename=path2, settings_filename=settings)
    #track_gui(movie_filename="testdata/hydrogel.mp4",settings_filename = "testdata/temp.param")
