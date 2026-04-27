from particletracker import track_gui, batchprocess
import os


if __name__ == '__main__':

  


    path1 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\4K_50p\\700-600Q\\"
    #path2 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\4K_50p\\625\\"
    path3 = "E:\\RawData\\Joe\\grain_boundarys\\Triple_H\\82g\\4K_50p\\700-650Q\\"
    settings = "E:\\RawData\\Joe\\grain_boundarys\\3_crystal_noGB_Q.param"

    #for path in [path1, path3]:
    #  batchprocess(path+"*.MP4", settings)
    #  print(path + " done")

   
    #batchprocess(path+"*.MP4", settings)
    track_gui()




