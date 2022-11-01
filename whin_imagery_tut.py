#%%
import cv2
import numpy as np
# Loading exposure images into a list
img_fn = ["img0.jpeg", "img1.jpeg", "img2.jpeg", "img3.jpeg"]
whin_list=["/Users/jhasneha/Documents/fall2021/DOE/ACRE/2020-09-15/lwir/20200915N6491513320616TDK9979.jp2","/Users/jhasneha/Documents/fall2021/DOE/ACRE/2020-09-15/bgrn/20200915N6491513320616TDK9979.jp2"]
img_list = [cv2.imread(fn) for fn in whin_list]

#img_list = [cv2.imread(fn) for fn in img_fn]
#exposure_times = np.array([15.0], dtype=np.float32)
#exposure_times = np.array([15.0, 2.5, 0.25, 0.0333], dtype=np.float32)


#%%
#Merge exposures to HDR image
merge_debvec = cv2.createMergeDebevec()
hdr_debvec=merge_debvec.process(img_list,times=exposure_times.copy())
merge_robertson=cv2.createMergeRobertson()
hdr_robertson=merge_robertson.process(img_list, times=exposure_times.copy())


#%%
#tonemap HDR image
tonemap1=cv2.createTonemap(2.2)
res_debvec=tonemap1.process(hdr_debvec.copy())
tonemap2= cv2.createTonemap(1.3)
res_robertson=tonemap2.process(hdr_robertson.copy())


#%%
#exposure fusion using Mertens
merge_mertens=cv2.createMergeMertens()
res_mertens=merge_mertens.process(img_list)



#%%
#convert datatype to 8 bit and save 
#res_debvec_8bit = np.clip(res_debvec*255,0,255).astype('uint8')
#res_robertson_8bit = np.clip(res_robertson*255,0,255).astype('uint8')
res_mertens_8bit = np.clip(res_mertens*255,0,255).astype('uint8')

#cv2.imwrite("ldr_debvec.jpg", res_debvec_8bit)
#cv2.imwrite("ldr_robertson.jpg", res_robertson_8bit)
cv2.imwrite("ldr_mertens.jpg", res_mertens_8bit)







#%%
from skimage import io
import numpy as np
from matplotlib import pyplot as plt
import cv2 

#my_img=io.imread("/Users/jhasneha/Documents/DOE/summer2021/DOE_ag/UAV_image_tut/img0.jpeg")
my_img_cv2=cv2.imread("/Users/jhasneha/Documents/fall2021/DOE/ACRE/2020-07-29/bgrn/20200729N6491518213316TEK0080.jp2")

print (my_img_cv2)
#print(my_img_cv2)
# %%
plt.imshow(my_img_cv2)
#plt.imshow(my_img)
# cv2.imshow("cv2_image",my_img_cv2)
# k=cv2.waitKey(0)
# if k == 27 or k == ord('q'):
#     cv2.destroyAllWindows()




#%%
import cv2
# Convert
image = cv2.imread('/Users/jhasneha/Documents/fall2021/DOE/ACRE/2020-07-29/bgrn/20200729N6491518213316TEK0080.jp2')

cv2.imwrite('test_convert.png', image)
#jpg_imglist=[cv2.imwrite(fn) for fn in ]


#%%
import os
import pathlib
rootfilepath="/Users/jhasneha/Documents/fall2021/DOE/ACRE/2020-07-29"
files=os.listdir(rootfilepath)
for entry in files:
    if not entry.startswith('.'):
        print("image type",entry)
        new_root=rootfilepath + '/' + entry
        pattern="*.jp2"
        list_img=list(pathlib.Path(new_root).glob(pattern))
        print(list_img[0])

#%%
img_list = [cv2.imread(fn) for fn in list_img]
img_list_dec=cv2.imdecode(img_list)



#%%

# %%


# %%
# %%
