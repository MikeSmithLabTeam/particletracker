from src.particletracker import track_gui, batchprocess
import os


if __name__ == '__main__':

  


    path1 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\new_code_tests\\84g_550_static\\"
    #path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\4K_50p\\625\\"
    path3 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\4K_50p\\700-650Q\\"
    settings = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\new_code_tests\\84g_550_static\\test.param"

    #batchprocess(path1+"*.MP4", settings)

    #for path in [path1, path3]:
      #batchprocess(path+"*.MP4", settings)
      #print(path + " done")

   
    #batchprocess(path+"*.MP4", settings)
    track_gui()