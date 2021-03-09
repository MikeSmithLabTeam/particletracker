from labvision.video.opencv_io import ReadVideo
from labvision.images import display, save
import numpy as np



filename=r'C:\\Users\\ppzmis\\OneDrive - The University of Nottingham\\Documents\\charge.mp4'

readvid=ReadVideo(filename)

img = readvid.read_frame(n=0)
img2 = readvid.read_frame(n=1)

output_img = np.zeros(np.shape(img), dtype=np.uint8)
output_img[500:,:] = img[500:,:]
output_img[0:500,:] = img2[0:500,:]

print(np.shape(output_img))

display(output_img)
save(output_img,filename[:-4] + 'charge_bkgimg.png' )


