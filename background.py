from labvision.video.opencv_io import ReadVideo
from labvision.images import display, save
import numpy as np



filename=r'C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\Teaching\\3rd and 4th yr lab projects\\yr4granularCharging\\processed videos\\processed videos\\11.03_uncharged_bead_and_plate2_processed.mp4'

readvid=ReadVideo(filename)

img = readvid.read_frame(n=1)
img2 = readvid.read_frame(n=2)

output_img = np.zeros(np.shape(img), dtype=np.uint8)
output_img[500:,:] = img2[500:,:]
output_img[:500,:] = img[:500,:]
#output_img[:500,:] = img[:500,:]
#output_img[500:,:] = img2[500:,:]



display(output_img)
save(output_img,filename[:-4] + '_bkgimg.png' )
#save(img, filename[:-4] + '_bkgimg.png')


